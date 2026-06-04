# Auto-generated Python from PYREACT server block
def get_user(user_id):
        users = {
            "1": {"id": "1", "name": "Budi Santoso", "role": "admin"},
            "2": {"id": "2", "name": "Ani Rahayu",  "role": "user"},
        }
        return users.get(user_id, {"error": "User not found"})

    def get_posts():
        return [
            {"id": 1, "title": "Mengenal PyReact",      "author": "Budi"},
            {"id": 2, "title": "Routing di PyReact",    "author": "Ani"},
            {"id": 3, "title": "Self-Healing Compiler", "author": "Budi"},
        ]
