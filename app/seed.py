from app.db.session import Base, engine
from datetime import datetime
from app.db.session import SessionLocal
from app.models.user import User
from app.models.team import Team
from app.models.idea import Idea
from app.models.task import Task
from app.core.security import hash_password

def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:

        admin = db.query(User).filter_by(email="admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                name="Administrator",
                password_hash=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("[+] Admin user created")
        else:
            print("[=] Admin user already exists")

        team_names = ["Operations", "Engineering", "Quality"]
        teams = []

        for name in team_names:
            team = db.query(Team).filter_by(name=name).first()
            if not team:
                team = Team(name=name, description=f"{name} team for Kaizen activities")
                db.add(team)
                db.commit()
                db.refresh(team)
                print(f"[+] Team created: {name}")
            else:
                print(f"[=] Team already exists: {name}")

            teams.append(team)


        sample_idea = db.query(Idea).first()
        if not sample_idea:
            sample_idea = Idea(
                title="Reduce waste in documentation process",
                description="Improve SOP writing workflow to cut approval time by 20%.",
                status="submitted",
                creator_id=admin.id,
                team_id=teams[0].id,
            )
            db.add(sample_idea)
            db.commit()
            print("[+] Sample idea created")
        else:
            print("[=] Sample idea already exists")

        sample_task = db.query(Task).first()
        if not sample_task:
            sample_task = Task(
                title="Create new SOP template",
                description="Cleaner SOP template to reduce writing time.",
                status="in_progress",
                assignee_id=admin.id,
                idea_id=sample_idea.id,
            )
            db.add(sample_task)
            db.commit()
            print("[+] Sample task created")
        else:
            print("[=] Sample task already exists")

        print("\n Seed completed successfully.")


    finally:
        db.close()



if __name__ == "__main__":
    run_seed()
