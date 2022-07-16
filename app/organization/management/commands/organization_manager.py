from django.core.management.base import BaseCommand

from organization.services.organization_service import OrganizationService


class Command(BaseCommand):
    help = "Organization Manager"

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--initiate",
            action="store_true",
            help="Create a schema.",
        )
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            help="Delete a organization.",
        )
        parser.add_argument(
            "-ud",
            "--undelete",
            action="store_true",
            help="UnDelete a organization.",
        )

        parser.add_argument(
            "--schema_name",
            help="Specify a schema name.",
        )
        parser.add_argument(
            "--organization_id",
            help="Specify a organization id.",
        )
        parser.add_argument(
            "--organization_name",
            help="Specify a organization name.",
        )
        parser.add_argument(
            "--email",
            help="Specify an email.",
        )
        parser.add_argument(
            "--password",
            help="Specify a password.",
        )

    def handle(self, *args, **options):
        if options.get("i") or options.get("initiate"):
            if (
                options.get("schema_name")
                and options.get("organization_name")
                and options.get("email")
                and options.get("password")
            ):
                schema_name = options.get("schema_name")
                organization_name = options.get("organization_name")
                email = options.get("email")
                password = options.get("password")

                organization_service = OrganizationService()
                result, _, _ = organization_service.initiate_schema(
                    schema_name=schema_name,
                    organization_name=organization_name,
                    email=email,
                    password=password,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully initiate a schema!")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS("Can not initiate a schema!"))
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        elif options.get("c") or options.get("create"):
            if options.get("schema_name") and options.get("organization_name"):
                schema_name = options.get("schema_name")
                organization_name = options.get("organization_name")

                organization_service = OrganizationService()
                result, _ = organization_service.create_organization(
                    schema_name=schema_name,
                    organization_name=organization_name,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully create a organization!")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS("Can not create a organization!")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        elif options.get("d") or options.get("delete"):
            if options.get("schema_name") and options.get("organization_id"):
                schema_name = options.get("schema_name")
                organization_id = options.get("organization_id")

                organization_service = OrganizationService()
                result = organization_service.delete_organization(
                    schema_name=schema_name,
                    organization_id=organization_id,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully delete a organization!")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS("Can not delete a organization!")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        elif options.get("ud") or options.get("undelete"):
            if options.get("schema_name") and options.get("organization_id"):
                schema_name = options.get("schema_name")
                organization_id = options.get("organization_id")

                organization_service = OrganizationService()
                result = organization_service.undelete_organization(
                    schema_name=schema_name,
                    organization_id=organization_id,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully undelete a organization!")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS("Can not undelete a organization!")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        else:
            self.stdout.write(self.style.ERROR("Please provide the correct option."))
