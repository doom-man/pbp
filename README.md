# pbp

lldb 可以对未加载模块的符号下断点，无法对未加载模块的偏移下断点。

仅支持android


![image-20230105181844505](http://oss.pareto.fun/img/image-20230105181844505.png)

该插件实现在未加载模块的偏移处断点。



## 使用说明

```bash
command script i /path/to/script
pbp libxxx.so 0x123
c
```

恢复程序正常运行。



## 演示效果

![image-20230124180651960](README.assets/image-20230124180651960.png)

