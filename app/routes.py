from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models import Post
from app.schemas import PostCreate, PostUpdate, PostResponse
from pydantic import ValidationError

posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')


@posts_bp.route('', methods=['GET'])
def get_posts():
    try:
        posts = db.session.query(Post).all()
        return jsonify([PostResponse.model_validate(post).model_dump() for post in posts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = db.session.get(Post, post_id)
        if post is None:
            return jsonify({'error': 'Post not found'}), 404
        return jsonify(PostResponse.model_validate(post).model_dump()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posts_bp.route('', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        post_data = PostCreate.model_validate(data)
        
        post = Post(
            title=post_data.title,
            content=post_data.content
        )
        db.session.add(post)
        db.session.commit()
        
        return jsonify(PostResponse.model_validate(post).model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        post = db.session.get(Post, post_id)
        if post is None:
            return jsonify({'error': 'Post not found'}), 404
        
        data = request.get_json()
        post_data = PostUpdate.model_validate(data)
        
        if post_data.title is not None:
            post.title = post_data.title
        if post_data.content is not None:
            post.content = post_data.content
        
        db.session.commit()
        
        return jsonify(PostResponse.model_validate(post).model_dump()), 200
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        post = db.session.get(Post, post_id)
        if post is None:
            return jsonify({'error': 'Post not found'}), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

