import { Command, CommandRunner, Option } from 'nest-commander';
import { CliService } from 'src/services/cli.service';

interface CreateAdminApiKeyOptions {
  name?: string;
  permissions?: string;
  userEmail?: string;
  userId?: string;
  check?: boolean;
}

@Command({
  name: 'create-api-key',
  description: 'Create an API key for a user. If no user is specified, creates one for the first admin user.',
  options: { isDefault: false },
})
export class CreateAdminApiKeyCommand extends CommandRunner {
  constructor(private service: CliService) {
    super();
  }

  async run(passedParams: string[], options: CreateAdminApiKeyOptions): Promise<void> {
    try {
      const keyName = options.name || 'Admin CLI Key';
      const permissions = options.permissions || 'all';
      const useAllPermissions = permissions === 'all';
      
      const result = await this.service.createAdminApiKey(
        keyName,
        permissions,
        useAllPermissions,
        options.userEmail,
        options.userId,
        options.check
      );

      if ('existing' in result && result.existing) {
        return;
      }

      // TypeScript knows result must have secret property here
      console.log((result as { secret: string; apiKey: any }).secret);
    } catch (error) {
      console.error(error);
      console.error('Unable to create admin API key');
    }
  }

  @Option({
    flags: '-n, --name <name>',
    description: 'Name for the API key (default: "Admin CLI Key")',
  })
  parseName(value: string): string {
    return value;
  }

  @Option({
    flags: '-p, --permissions <permissions>',
    description: 'Permissions for the API key. Use "all" for all permissions, or comma-separated list (default: "all")',
  })
  parsePermissions(value: string): string {
    return value;
  }

  @Option({
    flags: '-e, --user-email <email>',
    description: 'Email of the user to create the API key for',
  })
  parseUserEmail(value: string): string {
    return value;
  }

  @Option({
    flags: '-u, --user-id <id>',
    description: 'ID of the user to create the API key for',
  })
  parseUserId(value: string): string {
    return value;
  }

  @Option({
    flags: '-c, --check',
    description: 'Only create the API key if one with the same name does not already exist',
  })
  parseCheck(): boolean {
    return true;
  }
}
