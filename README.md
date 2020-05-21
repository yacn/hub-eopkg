# hub-eopkg

Solus eopkg config for [github/hub](https://github.com/github/hub)

## Building yourself

### Requirements

You've set up a Solus packaging directory according to this document:
https://getsol.us/articles/packaging/building-a-package/en/

Assuming `$SOLUS_PKG_DIR` points to your packaging directory with `common`
already cloned:

```
$ git clone https://github.com/yacn/hub-eopkg.git "$SOLUS_PKG_DIR/hub"
$ cd "$SOLUS_PKG_DIR"
$ echo "include ../Makefile.common" > Makefile
$ make
$ ls *.eopkg
```

## Refreshing `package.yml`

To determine latest version and bump release in package.yml

```
$ ./refresh.py
```

If you already have the tag and release:

```
$ ./update-package-yml.sh $tag $release < package.yml > package.yml.tmp
$ mv package.yml{.tmp,}
```
