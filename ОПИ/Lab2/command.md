### GIT BASH:
```
rm -rf repo .git wc .rotter* 2>/dev/null
bash git.sh
bash svn.sh

# 运行完验证
# Git
git log --graph --oneline --all

# SVN
svn log -v file:///$(pwd)/repo
```