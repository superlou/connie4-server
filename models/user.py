from sqlmodel import SQLModel, Field, Session


class User(SQLModel, table=True):
    email: str = Field(primary_key=True)
    google_access_token: str = Field()

    def create_or_update(self, session: Session):
        existing = session.get(User, self.email)
        if existing:
            existing.google_access_token = self.google_access_token
            session.commit()
        else:
            session.add(self)
            session.commit()

        print(self)