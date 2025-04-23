import subprocess
import os
import sys

import tiktoken
from openai import OpenAI
client = OpenAI()

def clone_git_repo(repo_url, branch, target_dir):
    cmd = ["git", "clone", "-b", branch, repo_url, target_dir]
    subprocess.run(cmd, check=True)

def diff_changes(repo_dir, old_branch, new_branch, file_path):
    cmd = ["git", "-C", repo_dir, "diff", f"{old_branch}..{new_branch}", file_path,
           ":(exclude)*uv.lock",
           ":(exclude)*package-lock.json"
    ]
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def get_file_content(file_path):
    with open(f"../{file_path}", 'r') as file:
        return file.read()
    
def write_file_content(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def count_tokens(text):
    # o4-mini is not supported yet, so we use o3-mini for now. This is close enough.
    encoding = tiktoken.encoding_for_model("o3-mini")
    return len(encoding.encode(text))

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

    input_prompt = f"""
        You are a software engineer that maintains a package called Immich Distribution.
        Immich Distribution is a snap package that packages the software Immich.
        The package is using Immich {old_release} currently and is going to upgrade to Immich {new_release}.
        You are provided a diff of changes between the old version and the new version.
        Your job is to figure out if the changes are relevant to the files you maintain in the package.

        Formatting of the response:
        - Your response should be formatted in markdown to fit in a GitHub comment.
        - You must provide code diffs of what needs to be changed.
        - Keep the diffs as small as possible.
        - You must provide a short explanation of why the change is needed.
        - You must provide a short explanation of what the change is doing.
        - Diffs should be sounded by triple backticks.
        - Do not mention files where there are no changes needed.
        - You will not fix existing bugs in the code, only things related to the upgrade.
        - Generate unified diffs for the files that need to be changed.
        - It's really important that the diffs are valid and applies to the provided files.

        {prompt}

        Give advice on what I need to change in the following files:
        {", ".join(relevant_files)}
        
        Files that has changed in the new release of Immich:
        {diff_changes_output}

        The package contains the following relevant files:
        {relevant_files_content}
        """

    token_count = count_tokens(input_prompt)
    print(f"Input prompt token count: {token_count}")
    
    chat_response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": input_prompt}]
    )
    response_text = chat_response.choices[0].message.content

    os.makedirs("reports", exist_ok=True)
    write_file_content(report_file, response_text)

def concat_files(folder_path):
    content = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as f:
                    content.append(f"\n=== FILE: {filename} ===")
                    content.append(f.read())
                    content.append("\n")
    return "\n\n".join(content)


def main():
    # Get old and new versions from command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python main.py <old_version> <new_version>")
        print("Example: python main.py v1.130.3 v1.131.3")
        sys.exit(1)
    
    old_release = sys.argv[1]
    new_release = sys.argv[2]

    # Clone the repository if the directory doesn't exist
    repo_remote = "https://github.com/immich-app/immich.git"
    repo_local = "immich"
    
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

    generate_report("ml-start", repo_local, old_release, new_release, "machine-learning",
        [
            "src/bin/immich-machine-learning",
            "src/bin/load-env",
        ],
        """
        - The "immich-machine-learning" script is the entry point for the machine learning service.
        - Upstream Immich uses __main__.py to start the application.

        We are using our own script with a few changes adapted to our needs. Make sure that any changes
        done in the upstream package do not need to be applied to the "immich-machine-learning" script.
        """
    )


    if os.path.exists("final_report.md"):
        print("Final report already exists. Skipping generation.")
    else:
        print("Generating final report...")

        response = client.responses.create(
            model="o4-mini",
            input=f"""
                You are a software engineer that maintains a package called Immich Distribution that packages the software Immich.
                You are given a set of reports that contains the changes needed to upgrade the package from Immich {old_release} to {new_release}.
                Your job is to generate a final report that contains all the changes needed to upgrade the package.

                Formatting of the response:                
                - Please make a nicely formatted report.
                - You must provide code diffs of what needs to be changed.
                - Keep the diffs as small as possible.
                - Remove unnecessary lines from the diffs.
                - Use unified diff format.
                - You must provide a short explanation of why the change is needed.
                
                The response should be formatted in markdown to fit in a GitHub comment.

                The reports are:
                {concat_files("reports")}
            """
        )

        write_file_content("final_report.md", response.output_text)


if __name__ == "__main__":
    main()
