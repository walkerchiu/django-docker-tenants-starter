from django.core.management.base import BaseCommand

from tenant.services.tenant_service import TenantService


class Command(BaseCommand):
    help = "Tenant Manager"

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--create",
            action="store_true",
            help="Create a tenant",
        )
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            help="Delete a tenant.",
        )
        parser.add_argument(
            "-ud",
            "--undelete",
            action="store_true",
            help="UnDelete a tenant.",
        )

        parser.add_argument(
            "--tenant_id",
            help="Specify a tenant id.",
        )
        parser.add_argument(
            "--organization_name",
            help="Specify a organization name.",
        )
        parser.add_argument(
            "--subdomain",
            help="Specify a subdomain.",
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
        if options.get("c") or options.get("create"):
            if (
                options.get("organization_name")
                and options.get("subdomain")
                and options.get("email")
                and options.get("password")
            ):
                organization_name = options.get("organization_name")
                subdomain = options.get("subdomain")
                email = options.get("email")
                password = options.get("password")

                tenant_service = TenantService()
                result = tenant_service.create_tenant(
                    organization_name=organization_name,
                    subdomain=subdomain,
                    email=email,
                    password=password,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully create a tenant!")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS("Can not create a tenant!"))
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        elif options.get("d") or options.get("delete"):
            if options.get("tenant_id"):
                tenant_id = options.get("tenant_id")

                tenant_service = TenantService()
                result = tenant_service.delete_tenant(
                    tenant_id=tenant_id,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully delete a tenant!")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS("Can not delete a tenant!"))
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        elif options.get("ud") or options.get("undelete"):
            if options.get("tenant_id"):
                tenant_id = options.get("tenant_id")

                organization_service = TenantService()
                result = organization_service.undelete_tenant(
                    tenant_id=tenant_id,
                )

                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Successfully undelete a tenant!")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS("Can not undelete a tenant!"))
            else:
                self.stdout.write(
                    self.style.ERROR("Please provide the correct option.")
                )

        else:
            self.stdout.write(self.style.ERROR("Please provide the correct option."))
