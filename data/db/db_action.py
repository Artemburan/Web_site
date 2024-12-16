from typing import List

from data.db.base import Session
from data.db.models import Author, Post


def get_authors() -> List[Author]:
    with Session() as session:
        return session.query(Author).all()


def get_author(id) -> Author:
    with Session() as session:
        return session.query(Author).where(Author.id == id).first()


def add_author(name, country) -> int:
    with Session() as session:
        author = Author(name=name, country=country)
        session.add(author)
        session.commit()
        session.refresh(author)
        return author.id


def del_author(id) -> None:
    with Session() as session:
        author = session.query(Author).filter_by(id=id).first()
        session.delete(author)
        session.commit()


def add_post(title, text, author_id) -> int:
    with Session() as session:
        post = Post(title=title, text=text, author_id=author_id)
        session.add(post)
        session.commit()
        session.refresh(post)
        return post.id


def get_posts() -> List[Post]:
    with Session() as session:
        posts = session.query(Post).all()
        return posts


def get_post(id) -> Post:
    with Session() as session:
        return session.query(Post).where(Post.id == id).first()


def del_post(id) -> None:
    with Session() as session:
        post = session.query(Post).filter_by(id=id).first()
        session.delete(post)
        session.commit()


def edit_post(id, title, text) -> None:
    with Session() as session:
        post = session.query(Post).where(Post.id == id).first()
        post.title = title
        post.text = text
        session.commit()