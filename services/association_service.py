from db.models.user_course_association import UserCourseAssociation


class AssociationService:
    def __init__(self, db):
        self.db = db

    def add_association(self, user_id: int, course_id: int) -> bool:
        """
        Adds an association between a user and a course if it doesn't already exist.
        """
        # Check if the association already exists
        exists = self.db.query(UserCourseAssociation).filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        if not exists:
            # Create a new association
            association = UserCourseAssociation(user_id=user_id, course_id=course_id)
            self.db.add(association)
            self.db.commit()
            return True
        return False

    def check_association(self, user_id: int, course_id: int) -> bool:
        """
        Checks if an association between a user and a course exists.
        """
        association = self.db.query(UserCourseAssociation).filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        return association is not None

    def remove_association(self, user_id: int, course_id: int) -> bool:
        """
        Removes an association between a user and a course if it exists.
        """
        association = self.db.query(UserCourseAssociation).filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        if association:
            self.db.delete(association)
            self.db.commit()
            return True
        return False
