from flask import Flask, request, jsonify
from py2neo import Graph, Node, Relationship
import uuid
import time

app = Flask(__name__)

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

@app.route('/')
def index():
    return "Bienvenue sur l'API Neo4j !"

### --- UTILISATEURS ---

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if "name" not in data or "email" not in data:
        return jsonify({"error": "Champs 'name' et 'email' requis"}), 400
    user = Node("User", id=str(uuid.uuid4()), name=data["name"], email=data["email"], created_at=time.time())
    graph.create(user)
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = graph.run("MATCH (u:User) RETURN u").data()
    return jsonify([dict(record['u']) for record in users]), 200

@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = graph.run("MATCH (u:User {id: $id}) RETURN u", id=id).evaluate()
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    return jsonify(dict(user)), 200

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    data = request.json
    graph.run("MATCH (u:User {id: $id}) SET u.name = $name, u.email = $email", id=id, name=data["name"], email=data["email"])
    return jsonify({"message": "Utilisateur mis à jour"}), 200

@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    graph.run("MATCH (u:User {id: $id}) DETACH DELETE u", id=id)
    return jsonify({"message": "Utilisateur supprimé"}), 200

@app.route('/users/<id>/friends', methods=['GET'])
def get_friends(id):
    friends = graph.run("""
        MATCH (u:User {id: $id})-[:FRIENDS_WITH]-(f:User)
        RETURN f
    """, id=id).data()
    return jsonify([dict(record['f']) for record in friends]), 200

@app.route('/users/<id>/friends', methods=['POST'])
def add_friend(id):
    friend_id = request.json.get("friend_id")
    graph.run("""
        MATCH (u1:User {id: $id}), (u2:User {id: $friend_id})
        MERGE (u1)-[:FRIENDS_WITH]-(u2)
    """, id=id, friend_id=friend_id)
    return jsonify({"message": "Ami ajouté"}), 200

@app.route('/users/<id>/friends/<friend_id>', methods=['DELETE'])
def remove_friend(id, friend_id):
    graph.run("""
        MATCH (u1:User {id: $id})-[r:FRIENDS_WITH]-(u2:User {id: $friend_id})
        DELETE r
    """, id=id, friend_id=friend_id)
    return jsonify({"message": "Ami supprimé"}), 200

@app.route('/users/<id>/friends/<friend_id>', methods=['GET'])
def are_friends(id, friend_id):
    result = graph.run("""
        MATCH (u1:User {id: $id})-[r:FRIENDS_WITH]-(u2:User {id: $friend_id})
        RETURN r
    """, id=id, friend_id=friend_id).evaluate()
    return jsonify({"are_friends": result is not None}), 200

@app.route('/users/<id>/mutual-friends/<other_id>', methods=['GET'])
def mutual_friends(id, other_id):
    mutual = graph.run("""
        MATCH (a:User {id: $id})-[:FRIENDS_WITH]-(f:User)-[:FRIENDS_WITH]-(b:User {id: $other_id})
        RETURN f
    """, id=id, other_id=other_id).data()
    return jsonify([dict(record['f']) for record in mutual]), 200

### --- POSTS ---

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = graph.run("MATCH (p:Post) RETURN p").data()
    return jsonify([dict(record['p']) for record in posts]), 200

@app.route('/posts/<id>', methods=['GET'])
def get_post(id):
    post = graph.run("MATCH (p:Post {id: $id}) RETURN p", id=id).evaluate()
    if not post:
        return jsonify({"error": "Post non trouvé"}), 404
    return jsonify(dict(post)), 200

@app.route('/users/<user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    posts = graph.run("""
        MATCH (u:User {id: $user_id})-[:CREATED]->(p:Post)
        RETURN p
    """, user_id=user_id).data()
    return jsonify([dict(record['p']) for record in posts]), 200

@app.route('/users/<user_id>/posts', methods=['POST'])
def create_post(user_id):
    data = request.json
    user = graph.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id).evaluate()
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    post = Node("Post", id=str(uuid.uuid4()), title=data["title"], content=data["content"], created_at=time.time())
    graph.create(post)
    graph.create(Relationship(user, "CREATED", post))
    return jsonify({"message": "Post créé"}), 201

@app.route('/posts/<id>', methods=['PUT'])
def update_post(id):
    data = request.json
    graph.run("MATCH (p:Post {id: $id}) SET p.title = $title, p.content = $content", id=id, title=data["title"], content=data["content"])
    return jsonify({"message": "Post mis à jour"}), 200

@app.route('/posts/<id>', methods=['DELETE'])
def delete_post(id):
    graph.run("MATCH (p:Post {id: $id}) DETACH DELETE p", id=id)
    return jsonify({"message": "Post supprimé"}), 200

@app.route('/posts/<id>/like', methods=['POST'])
def like_post(id):
    user_id = request.json.get("user_id")
    graph.run("""
        MATCH (u:User {id: $user_id}), (p:Post {id: $post_id})
        MERGE (u)-[:LIKES]->(p)
    """, user_id=user_id, post_id=id)
    return jsonify({"message": "Like ajouté"}), 200

@app.route('/posts/<id>/like', methods=['DELETE'])
def unlike_post(id):
    user_id = request.json.get("user_id")
    graph.run("""
        MATCH (u:User {id: $user_id})-[l:LIKES]->(p:Post {id: $post_id})
        DELETE l
    """, user_id=user_id, post_id=id)
    return jsonify({"message": "Like supprimé"}), 200

### --- COMMENTAIRES ---

@app.route('/posts/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = graph.run("""
        MATCH (p:Post {id: $post_id})-[:HAS_COMMENT]->(c:Comment)
        RETURN c
    """, post_id=post_id).data()
    return jsonify([dict(record['c']) for record in comments]), 200

@app.route('/posts/<post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.json
    user = graph.run("MATCH (u:User {id: $id}) RETURN u", id=data["user_id"]).evaluate()
    post = graph.run("MATCH (p:Post {id: $id}) RETURN p", id=post_id).evaluate()
    if not user or not post:
        return jsonify({"error": "Utilisateur ou post introuvable"}), 404
    comment = Node("Comment", id=str(uuid.uuid4()), content=data["content"], created_at=time.time())
    graph.create(comment)
    graph.create(Relationship(user, "CREATED", comment))
    graph.create(Relationship(post, "HAS_COMMENT", comment))
    return jsonify({"message": "Commentaire ajouté"}), 201

@app.route('/comments', methods=['GET'])
def get_all_comments():
    comments = graph.run("MATCH (c:Comment) RETURN c").data()
    return jsonify([dict(record['c']) for record in comments]), 200

@app.route('/comments/<id>', methods=['GET'])
def get_comment(id):
    comment = graph.run("MATCH (c:Comment {id: $id}) RETURN c", id=id).evaluate()
    if not comment:
        return jsonify({"error": "Commentaire non trouvé"}), 404
    return jsonify(dict(comment)), 200

@app.route('/comments/<id>', methods=['PUT'])
def update_comment(id):
    data = request.json
    graph.run("MATCH (c:Comment {id: $id}) SET c.content = $content", id=id, content=data["content"])
    return jsonify({"message": "Commentaire mis à jour"}), 200

@app.route('/comments/<id>', methods=['DELETE'])
def delete_comment(id):
    graph.run("MATCH (c:Comment {id: $id}) DETACH DELETE c", id=id)
    return jsonify({"message": "Commentaire supprimé"}), 200

@app.route('/comments/<id>/like', methods=['POST'])
def like_comment(id):
    user_id = request.json.get("user_id")
    graph.run("""
        MATCH (u:User {id: $user_id}), (c:Comment {id: $comment_id})
        MERGE (u)-[:LIKES]->(c)
    """, user_id=user_id, comment_id=id)
    return jsonify({"message": "Like ajouté"}), 200

@app.route('/comments/<id>/like', methods=['DELETE'])
def unlike_comment(id):
    user_id = request.json.get("user_id")
    graph.run("""
        MATCH (u:User {id: $user_id})-[l:LIKES]->(c:Comment {id: $comment_id})
        DELETE l
    """, user_id=user_id, comment_id=id)
    return jsonify({"message": "Like supprimé"}), 200

if __name__ == '__main__':
    app.run(debug=True)
