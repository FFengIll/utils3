# utils3

As the name: `utils for python3`.

We learn, we try, we code - again and again.

Why not use it directly (though/while we already know)?
Why not use one and only one copy?
Why not use it gracefully (pythonic)?

utils3 contain some out-box api with python features like file, serialize, timer and so on.
`All in one` and `All for convenience`.

> Minimize the api numbers, since it is just a util.
> Try the best to reduce external dependencies.
> Event, thread, process, network related must go with extra package, but we can optional install them.

# deploy
## install
~~`pip install utils3`~~

actually, it is a module for myself only (for now).

## test
`pytest utils3/`

all tests work on pytest, so it is also a demo project of `pytest` :-D

# bin
- utils3_code.py

# api
## data
- snapshot
  - need db, default `leveldb` (google)
  - try to use `decorator` to store input and output of the function which will be edited, interrupted and so on.
  - snapshot try to save history of io to short time cost and save durable data.
  - 基于python修饰器，将特定函数的输入（参数）和输出（返回值）持久化存储在数据库中（默认使用简单的文件数据库leveldb）
- encode
  - detect the encode mode if we can
- indent & printer
  - control the print format
- convert
  - any thing to any other thing if we can

## cli
- arguments
  - use python `click`
- logger
  - get any logger quickly and simply


## file
- hash file
-

## serialize

## strings

## hash
- see `file`
-
