### Credit to: [cyclotruc](https://github.com/cyclotruc/gitingest)

For the creation of gitingest.

<hr>

I modifed the `ingest()` function to take in an additional parameter `remove_git` which recieves a boolean argument (default=False).

This argument is then passed to the `clone_repo()` function where upon completion of cloning the repository and the argument being True, the read_only access of the `.git/` is removed and then the folder itself is removed.
