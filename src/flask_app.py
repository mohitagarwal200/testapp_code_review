from flask import Flask, request, jsonify
from rich import print

from db import (
    get_challenges_for_candidate,
    get_users,
    get_user_by_cpf,
    create_user,
    update_user,
    delete_user,
)
from models import User

app = Flask(__name__)


@app.route("/")
def index():
    return (
        "Hi 👋 head out to "
        '<a href="/challenges/111.111.111-11">this link</a> to get started.'
    )


@app.route("/challenges/<cpf>")
def get_challenges(cpf: str):
    print(f"[bold]{'-' * 50}[/bold]")
    print(f"[bold]Passing input:[/bold] [yellow]{cpf}[/yellow]")

    challenges = get_challenges_for_candidate(cpf)
    output = [f"<li>{title}: scored {score}</li>" for title, score in challenges]

    disclaimer = f"""
        <p>Here are the challenges I got for candidate:
            <pre><blockquote>{cpf}</blockquote></pre>
        </p>
    """
    return f"{disclaimer}<br/><h3>Results</h3><ol>{''.join(output)}</ol>"


@app.route("/users", methods=["GET", "POST"])
def users_route():
    if request.method == "GET":
        users = get_users()
        return jsonify(users)
    elif request.method == "POST":
        data = request.get_json()
        new_user = User(
            id=None,
            cpf=data["cpf"],
            email=data["email"],
            birth_date=data.get("birth_date"),
            phone_number=data.get("phone_number"),
        )
        user = create_user(new_user)
        return jsonify(user)


@app.route("/users/<cpf>", methods=["GET", "PUT", "DELETE"])
def user_route(cpf: str):
    if request.method == "GET":
        user = get_user_by_cpf(cpf)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    elif request.method == "PUT":
        data = request.get_json()
        updated_user = update_user(cpf, data)
        if updated_user:
            return jsonify(updated_user)
        return jsonify({"error": "User not found"}), 404
    elif request.method == "DELETE":
        if delete_user(cpf):
            return jsonify({"message": "User deleted successfully"})
        return jsonify({"error": "User not found"}), 404
