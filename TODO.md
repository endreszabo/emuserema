consider supporting fzf:

```sh
cat .wssh_commands | fzf --multi --ansi --scroll-off=5 --height=10 --border=double --border-label-pos=-3:bottom --color=label:italic:black --tac --prompt=SSH\ to:\  --marker=✓ --layout=reverse --info=hidden --pointer=➜
```
