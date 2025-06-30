import os
import subprocess

def repo_cloner():
    # List of repositories
    repos = [
    "https://github.com/jankotek/MapDB.git",
    "https://github.com/mcMMO-Dev/mcMMO.git",
    "https://github.com/thinkaurelius/titan.git"
    ]

    os.chdir("/Users/jeancarlorspaul/IdeaProjects")

    print(os.getcwd())


    # Clone each repository
    for repo in repos:
        try:
            print(f"Cloning {repo}...")
            subprocess.run(["git", "clone", repo], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {repo}: {e}")

def mvn_check():
    env = os.environ.copy()
    jdk_path = '/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home'
    mvn_path = '/usr/local/opt/maven@3.6'

    # environment setting
    env["JAVA_HOME"] = jdk_path
    env["PATH"] = f"{jdk_path}/bin:" + env["PATH"]
    env["PATH"] = f"{mvn_path}/bin:" + env["PATH"]

    commit_version = "495402f9a8d764aa03c66ae0dd58b18413d3558e"
    local_repository_path = "/Users/jeancarlorspaul/IdeaProjects/titan"
    subprocess.run(['git', '-C', local_repository_path, 'reset', '--hard', commit_version], env=env)
    subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'clean'], env=env, capture_output=True, text=True)
    output = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'compile'], env=env, capture_output=True, text=True)
    print(output.stdout)
mvn_check()