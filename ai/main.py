import subprocess
import os

from openai import OpenAI
client = OpenAI()

def clone_git_repo(repo_url, branch, target_dir):
    cmd = ["git", "clone", "-b", branch, repo_url, target_dir]
    subprocess.run(cmd, check=True)

def diff_changes(repo_dir, old_branch, new_branch, file_path):
    cmd = ["git", "-C", repo_dir, "diff", f"{old_branch}..{new_branch}", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def get_file_content(file_path):
    with open(f"../{file_path}", 'r') as file:
        return file.read()
    
def write_file_content(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def generate_report(report_name, repo_local, old_release, new_release, diff_path, relevant_files, prompt):

    report_file = f"reports/{report_name}.md"
    if os.path.exists(report_file):
        print(f"Report {report_file} already exists. Skipping generation.")
        return
    print(f"Generating report {report_file}...")

    relevant_files_content = ""
    for file in relevant_files:
        content = get_file_content(file)
        relevant_files_content += f"\n\n{file}:\n{content}"

    diff_changes_output = diff_changes(repo_local, old_release, new_release, diff_path)

    response = client.responses.create(
        model="o3-mini",
        input=f"""
        You are a software engineer. You maintain a package of a piece of software called Immich.
        You are provided a diff of changes between the old version {old_release} and the new version {new_release}.
        Your job is to figure out if the changes are relevant to the files you maintain in the package.
        Your response should be formatted in markdown to fit in a GitHub comment.
        Give advice on what I need to change in the following files: {", ".join(relevant_files)}
        You must provide code diffs of what needs to be changed in the files.
        Diffs should be sounded by triple backticks.
        Omit files with no changes needed.
        You will not fix existing bugs in the code, only things related to the upgrade.
        Generate unified diffs for the files that need to be changed.
        It's really important that the diffs works and applies to the provided files.

        {prompt}
        
        Files that has changed in the new release of Immich:
        {diff_changes_output}

        The package contains the following relevant files:
        {relevant_files_content}
        """
    )

    os.makedirs("reports", exist_ok=True)
    write_file_content(report_file, response.output_text)

def concat_files(folder_path):
    content = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(root, filename)
                name = filename[:-3]  # Remove .md extension
                with open(file_path, 'r') as f:
                    content.append(f"## {name}\n\n{f.read()}")
    return "\n\n".join(content)


def main():

    # Clone the repository if the directory doesn't exist
    repo_remote = "https://github.com/immich-app/immich.git"
    repo_local = "immich"
    
    new_release = "v1.131.3"
    old_release = "v1.130.3"

    if not os.path.exists(repo_local):
        clone_git_repo(repo_remote, new_release, repo_local)

    generate_report("machine-learning", repo_local, old_release, new_release, "machine-learning",
        [
            "snap/snapcraft.yaml",
            "src/bin/immich-machine-learning",
            "src/bin/load-env",
        ],
        """
        snapcraft.yaml: This file is used to build the snap package for Immich. It contains the configuration for building the snap package, including the dependencies and build steps.
        src/bin/immich-machine-learning: This file is the entry point for the machine learning service. It contains the code that starts the service and loads the environment variables. Upstream start the application in a little different way so make sure this script start the application correctly.
        src/bin/load-env: This file is used to load the environment variables for the machine learning service. It contains the code that loads the environment variables from the .env file and sets them in the environment.
        """
    )

    generate_report("server", repo_local, old_release, new_release, "server",
        [
            "snap/snapcraft.yaml",
            "parts/immich-server/scripts/bin/immich-admin",
            "parts/immich-server/scripts/bin/immich-server",
        ],
        """
        snapcraft.yaml: This file is used to build the snap package for Immich. It contains the configuration for building the snap package, including the dependencies and build steps.
        parts/immich-server/scripts/bin/immich-admin: This file is the entry point for the Immich admin service. It contains the code that starts the service and loads the environment variables. Upstream start the application in a little different way so make sure this script start the application correctly.
        parts/immich-server/scripts/bin/immich-server: This file is the entry point for the Immich server service. It contains the code that starts the service and loads the environment variables. Upstream start the application in a little different way so make sure this script start the application correctly.
        """
    )

    generate_report("migrations", repo_local, old_release, new_release, "server/src/migrations",
        [
            "src/bin/sync-service.sh",
            "src/etc/modify-db.sql",
            "parts/sync/sync_service/main.py",
        ],
        """
        Make sure that there are no database migrations that will disturb the functionality of the sync service.
        Also make sure that modify-db.sql will work with the new migrations.
        """
    )

    generate_report("api", repo_local, old_release, new_release, "server",
        [
            "parts/sync/sync_service/main.py",
            "tests/test_sync.sh"
        ],
        """
        Make sure that there are no API changes that will disturb the functionality of the sync service.
        """
    )

    response = client.responses.create(
        model="o3-mini",
        input=f"""
            Please make a nicely formatted report of the following reports.
            I will add them as a comment to a pull request so please format it nicely with markdown.
            The reports are:
            
            {concat_files("reports")}
        """
    )

    if os.path.exists("final_report.md"):
        print("Final report already exists. Skipping generation.")
    else:
        print("Generating final report...")
        write_file_content("final_report.md", response.output_text)


if __name__ == "__main__":
    main()
