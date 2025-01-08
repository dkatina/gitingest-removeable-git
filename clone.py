import asyncio
import shutil
import os
import stat
from typing import Tuple

from gitingest.utils import async_timeout

CLONE_TIMEOUT = 20

def remove_readonly(func, path, excinfo):
    """
    Callback function for handling read-only files during shutil.rmtree.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

async def check_repo_exists(url: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "git",
        "ls-remote",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    return proc.returncode == 0

@async_timeout(CLONE_TIMEOUT)
async def clone_repo(query: dict, remove_git: bool) -> str:
    if not await check_repo_exists(query['url']):
        raise ValueError("Repository not found, make sure it is public")
        
    if query['commit']:
        print("COMMIT")
        proc = await asyncio.create_subprocess_exec(
            "git", 
            "clone",
            "--single-branch",
            query['url'],
            query['local_path'],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()


        
        proc = await asyncio.create_subprocess_exec(
            "git",
            "-C",
            query['local_path'],
            "checkout",
            query['branch'],
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE,
        )

        
        stdout, stderr = await proc.communicate()
    elif query['branch'] != 'main' and query['branch'] != 'master' and query['branch']:
        print("BRANCH")
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone", 
            "--depth=1",
            "--single-branch",
            "--branch",
            query['branch'],
            query['url'],
            query['local_path'],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    else:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            "--depth=1",
            "--single-branch",
            query['url'],
            query['local_path'],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    stdout, stderr = await proc.communicate()

    if proc.returncode == 0 and remove_git:
        git_folder_path = os.path.join(query['local_path'], '.git')

        try:
            if os.path.exists(git_folder_path):
                # Remove the .git folder with permission handling
                shutil.rmtree(git_folder_path, onerror=remove_readonly)
            
        except Exception as e:
            print(f"Error removing .git folder: {e}")
    else:
        print(f"Error cloning repository: {stderr.decode()}")
    
    return stdout, stderr   