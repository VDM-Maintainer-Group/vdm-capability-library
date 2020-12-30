# Note Film

**This capability aims at: allow to take notes on any application, any where, any time~**



### How to use

> **Structure**: N/A
>
> **Dependency**: N/A



### Capability Test
- [ ] record series of screenshots of **1920x1080 application**;
- [ ] take one screenshot as sample, run state-of-the-art similarity-check algorithm
- [ ] What's the best performance (fps) and resource usage at 10fps, under **CPU platform**?
- [ ] What's the best performance (fps) and resource usage at 10fps, under **GTX950M platform**?
- [ ] What's the best performance (fps) and resource usage at 10fps, under **GTX760 platform**?

### Timeline
- [ ] Capability Test
- [ ] Fork code of `deepin screen recorder`, https://github.com/linuxdeepin/deepin-screen-recorder.git
- [ ] Add `note film` button on `deepin-screen-recorder` and pass compile
- [ ] Add *screenshot* saving and indexing functions
- [ ] Implement **application preview** fetch real-time at 10fps (CPU-only)
- [ ] Implement similarity-check daemon with CUDA enabled
- [ ] display floating widget at proper position