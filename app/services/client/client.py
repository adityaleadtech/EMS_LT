# app/services/client/client.py

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client.client import Client
from app.models.ministry.ministry import Ministry
from app.models.client_ministries.client_ministries import ClientMinistry

from app.schemas.client.client import (
    ClientCreate,
    ClientUpdate,
)


class ClientService:

    # ---------------------------------------------------
    # Validators
    # ---------------------------------------------------

    @staticmethod
    def _validate_client_code(
        db: Session,
        client_code: str,
        exclude_client_id: Optional[str] = None,
    ):

        query = (
            db.query(Client)
            .filter(Client.client_code == client_code)
        )

        if exclude_client_id:
            query = query.filter(
                Client.id != exclude_client_id
            )

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client Code already exists."
            )

    @staticmethod
    def _validate_email(
        db: Session,
        email: str,
        exclude_client_id: Optional[str] = None,
    ):

        query = (
            db.query(Client)
            .filter(Client.email == email)
        )

        if exclude_client_id:
            query = query.filter(
                Client.id != exclude_client_id
            )

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )

    @staticmethod
    def _validate_phone(
        db: Session,
        phone: str,
        exclude_client_id: Optional[str] = None,
    ):

        query = (
            db.query(Client)
            .filter(Client.phone == phone)
        )

        if exclude_client_id:
            query = query.filter(
                Client.id != exclude_client_id
            )

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists."
            )

    # ---------------------------------------------------
    # Ministries
    # ---------------------------------------------------

    @staticmethod
    def _assign_ministries(
        db: Session,
        client_id: str,
        ministries: list[str],
    ):

        if not ministries:
            return

        for ministry_id in ministries:

            ministry = (
                db.query(Ministry)
                .filter(
                    Ministry.id == ministry_id,
                    Ministry.is_active == True,
                )
                .first()
            )

            if not ministry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ministry '{ministry_id}' not found."
                )

            db.add(
                ClientMinistry(
                    id=str(uuid.uuid4()),
                    client_id=client_id,
                    ministry_id=ministry.id,
                )
            )

    @staticmethod
    def _replace_ministries(
        db: Session,
        client_id: str,
        ministries: list[str],
    ):

        (
            db.query(ClientMinistry)
            .filter(
                ClientMinistry.client_id == client_id
            )
            .delete(synchronize_session=False)
        )

        ClientService._assign_ministries(
            db,
            client_id,
            ministries,
        )

    # ---------------------------------------------------
    # Create
    # ---------------------------------------------------

    @staticmethod
    def create_client(
        db: Session,
        payload: ClientCreate,
        created_by: str,
    ):

        try:

            ClientService._validate_client_code(
                db,
                payload.client_code,
            )

            ClientService._validate_email(
                db,
                payload.email,
            )

            ClientService._validate_phone(
                db,
                payload.phone,
            )

            client = Client(

                id=str(uuid.uuid4()),

                client_code=payload.client_code,
                client_name=payload.client_name,

                party=payload.party,

                email=payload.email,
                phone=payload.phone,

                is_mp=payload.is_mp,
                is_mla=payload.is_mla,
                is_minister=payload.is_minister,
                is_party_president=payload.is_party_president,

                constituency=payload.constituency,

                office_address=payload.office_address,

                state=payload.state,
                district=payload.district,
                city=payload.city,
                pincode=payload.pincode,

                office_logo=payload.office_logo,
                office_banner=payload.office_banner,

                description=payload.description,

                created_by=created_by,

                is_active=True,

                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            db.add(client)

            db.flush()

            ClientService._assign_ministries(
                db,
                client.id,
                payload.ministries,
            )

            db.commit()

            db.refresh(client)

            return client

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )
        # ---------------------------------------------------
    # Get By ID
    # ---------------------------------------------------

    @staticmethod
    def get_by_id(
        db: Session,
        client_id: str,
    ):

        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found."
            )

        return client

    # ---------------------------------------------------
    # Get All
    # ---------------------------------------------------

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ):

        query = db.query(Client)

        if is_active is not None:
            query = query.filter(
                Client.is_active == is_active
            )

        if search:

            query = query.filter(
                (
                    Client.client_name.ilike(f"%{search}%")
                )
                |
                (
                    Client.client_code.ilike(f"%{search}%")
                )
                |
                (
                    Client.email.ilike(f"%{search}%")
                )
                |
                (
                    Client.phone.ilike(f"%{search}%")
                )
                |
                (
                    Client.party.ilike(f"%{search}%")
                )
                |
                (
                    Client.constituency.ilike(f"%{search}%")
                )
            )

        total = query.count()

        clients = (
            query.order_by(
                Client.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
            "items": clients,
        }

    # ---------------------------------------------------
    # Update
    # ---------------------------------------------------

    @staticmethod
    def update(
        db: Session,
        client_id: str,
        payload: ClientUpdate,
    ):

        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found."
            )

        try:

            if (
                payload.client_code
                and payload.client_code != client.client_code
            ):

                ClientService._validate_client_code(
                    db,
                    payload.client_code,
                    client.id,
                )

            if (
                payload.email
                and payload.email != client.email
            ):

                ClientService._validate_email(
                    db,
                    payload.email,
                    client.id,
                )

            if (
                payload.phone
                and payload.phone != client.phone
            ):

                ClientService._validate_phone(
                    db,
                    payload.phone,
                    client.id,
                )

            update_data = payload.model_dump(
                exclude_unset=True,
                exclude={"ministries"},
            )

            for key, value in update_data.items():
                setattr(client, key, value)

            client.updated_at = datetime.now(
                timezone.utc
            )

            if payload.ministries is not None:

                ClientService._replace_ministries(
                    db,
                    client.id,
                    payload.ministries,
                )

            db.commit()

            db.refresh(client)

            return client

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=str(e),
            )

    # ---------------------------------------------------
    # Delete
    # ---------------------------------------------------

    @staticmethod
    def delete(
        db: Session,
        client_id: str,
    ):

        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found."
            )

        if not client.is_active:
            raise HTTPException(
                status_code=400,
                detail="Client already inactive."
            )

        client.is_active = False

        client.updated_at = datetime.now(
            timezone.utc
        )

        db.commit()

        return {
            "message": "Client deleted successfully."
        }

    # ---------------------------------------------------
    # Restore
    # ---------------------------------------------------

    @staticmethod
    def restore(
        db: Session,
        client_id: str,
    ):

        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found."
            )

        if client.is_active:
            raise HTTPException(
                status_code=400,
                detail="Client already active."
            )

        client.is_active = True

        client.updated_at = datetime.now(
            timezone.utc
        )

        db.commit()

        db.refresh(client)

        return client

    # ---------------------------------------------------
    # Ministries
    # ---------------------------------------------------

    @staticmethod
    def get_client_ministries(
        db: Session,
        client_id: str,
    ):

        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found."
            )

        data = (
            db.query(
                ClientMinistry,
                Ministry,
            )
            .join(
                Ministry,
                ClientMinistry.ministry_id == Ministry.id,
            )
            .filter(
                ClientMinistry.client_id == client_id
            )
            .all()
        )

        return [
            {
                "id": ministry.id,
                "ministry_name": ministry.ministry_name,
                "description": ministry.description,
            }
            for _, ministry in data
        ]

    @staticmethod
    def update_client_ministries(
        db: Session,
        client_id: str,
        ministries: list[str],
    ):

        client = (
            db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found."
            )

        ClientService._replace_ministries(
            db,
            client_id,
            ministries,
        )

        db.commit()

        return {
            "message": "Client ministries updated successfully."
        }