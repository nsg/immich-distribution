import { Injectable } from '@nestjs/common';
import { isAbsolute } from 'node:path';
import { SALT_ROUNDS } from 'src/constants';
import { UserAdminResponseDto, mapUserAdmin } from 'src/dtos/user.dto';
import { Permission } from 'src/enum';
import { BaseService } from 'src/services/base.service';

@Injectable()
export class CliService extends BaseService {
  async listUsers(): Promise<UserAdminResponseDto[]> {
    const users = await this.userRepository.getList({ withDeleted: true });
    return users.map((user) => mapUserAdmin(user));
  }

  async resetAdminPassword(ask: (admin: UserAdminResponseDto) => Promise<string | undefined>) {
    const admin = await this.userRepository.getAdmin();
    if (!admin) {
      throw new Error('Admin account does not exist');
    }

    const providedPassword = await ask(mapUserAdmin(admin));
    const password = providedPassword || this.cryptoRepository.randomBytesAsText(24);
    const hashedPassword = await this.cryptoRepository.hashBcrypt(password, SALT_ROUNDS);

    await this.userRepository.update(admin.id, { password: hashedPassword });

    return { admin, password, provided: !!providedPassword };
  }

  async disablePasswordLogin(): Promise<void> {
    const config = await this.getConfig({ withCache: false });
    config.passwordLogin.enabled = false;
    await this.updateConfig(config);
  }

  async enablePasswordLogin(): Promise<void> {
    const config = await this.getConfig({ withCache: false });
    config.passwordLogin.enabled = true;
    await this.updateConfig(config);
  }

  async grantAdminAccess(email: string): Promise<void> {
    const user = await this.userRepository.getByEmail(email);
    if (!user) {
      throw new Error('User does not exist');
    }

    await this.userRepository.update(user.id, { isAdmin: true });
  }

  async revokeAdminAccess(email: string): Promise<void> {
    const user = await this.userRepository.getByEmail(email);
    if (!user) {
      throw new Error('User does not exist');
    }

    await this.userRepository.update(user.id, { isAdmin: false });
  }

  async disableOAuthLogin(): Promise<void> {
    const config = await this.getConfig({ withCache: false });
    config.oauth.enabled = false;
    await this.updateConfig(config);
  }

  async enableOAuthLogin(): Promise<void> {
    const config = await this.getConfig({ withCache: false });
    config.oauth.enabled = true;
    await this.updateConfig(config);
  }

  async getSampleFilePaths(): Promise<string[]> {
    const [assets, people, users] = await Promise.all([
      this.assetRepository.getFileSamples(),
      this.personRepository.getFileSamples(),
      this.userRepository.getFileSamples(),
    ]);

    const paths = [];

    for (const person of people) {
      paths.push(person.thumbnailPath);
    }

    for (const user of users) {
      paths.push(user.profileImagePath);
    }

    for (const asset of assets) {
      paths.push(
        asset.originalPath,
        asset.sidecarPath,
        asset.encodedVideoPath,
        ...asset.files.map((file) => file.path),
      );
    }

    return paths.filter(Boolean) as string[];
  }

  async migrateFilePaths({
    oldValue,
    newValue,
    confirm,
  }: {
    oldValue: string;
    newValue: string;
    confirm: (data: { sourceFolder: string; targetFolder: string }) => Promise<boolean>;
  }): Promise<boolean> {
    let sourceFolder = oldValue;
    if (sourceFolder.startsWith('./')) {
      sourceFolder = sourceFolder.slice(2);
    }

    const targetFolder = newValue;
    if (!isAbsolute(targetFolder)) {
      throw new Error('Target media location must be an absolute path');
    }

    if (!(await confirm({ sourceFolder, targetFolder }))) {
      return false;
    }

    await this.databaseRepository.migrateFilePaths(sourceFolder, targetFolder);

    return true;
  }

  async createAdminApiKey(
    keyName: string = 'Admin CLI Key',
    permissionsString: string = '',
    useAllPermissions: boolean = false,
    userEmail?: string,
    userId?: string,
    checkExisting: boolean = false,
  ): Promise<{ secret: string; apiKey: any } | { existing: true }> {
    let targetUser;

    if (userEmail) {
      targetUser = await this.userRepository.getByEmail(userEmail);
      if (!targetUser) {
        throw new Error(`User with email '${userEmail}' not found`);
      }
    } else if (userId) {
      targetUser = await this.userRepository.get(userId, {});
      if (!targetUser) {
        throw new Error(`User with ID '${userId}' not found`);
      }
    } else {
      const admin = await this.userRepository.getAdmin();
      if (!admin) {
        throw new Error('No admin user found');
      }
      targetUser = admin;
    }

    // If check is enabled, look for existing key with same name
    if (checkExisting) {
      const existingKeys = await this.apiKeyRepository.getByUserId(targetUser.id);
      const existingKey = existingKeys.find(key => key.name === keyName);
      if (existingKey) {
        return { existing: true };
      }
    }

    let permissions: Permission[] = [];
    if (useAllPermissions) {
      permissions = [Permission.All];
    } else if (permissionsString.trim()) {
      const permissionStrings = permissionsString.split(',').map(p => p.trim()).filter(p => p);
      permissions = permissionStrings.map(p => p as Permission);
    }

    const secret = this.cryptoRepository.randomBytesAsText(32);
    const hashedSecret = this.cryptoRepository.hashSha256(secret);

    const apiKey = await this.apiKeyRepository.create({
      name: keyName,
      key: hashedSecret,
      userId: targetUser.id,
      permissions,
    });

    return { secret, apiKey };
  }

  cleanup() {
    return this.databaseRepository.shutdown();
  }
}
