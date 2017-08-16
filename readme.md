# C++ auto include

## Requirements

``` sh
$ apt install python-clang-4.0 libclang-4.0-dev
```

## How to Use

``` sh
$ python2 a.py < a.cpp
```

You can add your rules using the config file `~/.local/share/autoinclude/config.yaml`. See `config.yaml` for an example.

## Example

``` sh
$ cat a.cpp
int main() {
    double x;
    cin >> x;
    cout << sqrt(x) << endl;
    return 0;
}

$ python2 a.py < a.cpp
#include <iostream>
#include <cmath>
using namespace std;

$ python2 a.py -i a.cpp

$ cat a.cpp
#include <iostream>
#include <cmath>
using namespace std;
int main() {
    double x;
    cin >> x;
    cout << sqrt(x) << endl;
    return 0;
}

$ g++ a.cpp && echo 2 | ./a.out
1.41421
```

## 競合

-   <https://github.com/quark-zju/vim-cpp-auto-include>
-   <https://github.com/syohex/emacs-cpp-auto-include>

## 感想

主な用途は競プロを想定。
標準ライブラリのヘッダのincludeだけでなくてもっとなんでも挿入できる。
全部テンプレや全部snippetで対処するより自動で抜き差しさせた方がよいのではと思ったので勢いで作った。
削除が未実装だったり挿入位置が完全ではないのもあり、わざわざ乗り換えるほど便利かというとそうでもなさそう。
