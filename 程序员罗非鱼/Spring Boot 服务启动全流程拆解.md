视频链接：https://www.douyin.com/video/7694501169573465371  
索引文档：[index.md](index.md)

什么是 Spring Boot 后端服务跑起来？简单说，就是从执行 main 方法，到内嵌 Web 服务器监听端口，再到能接收并返回 HTTP 请求的完整过程。它看起来只有一行启动代码，背后却串起了配置加载、组件扫描、自动配置、依赖注入和请求分发。理解这条链路能帮你定位启动失败、端口冲突、Bean 找不到、接口四零四等问题。先看启动入口。Spring Boot 项目通常有一个带 @SpringBootApplication 的类，里面 main 方法调用 SpringApplication.run。这个注解组合了三件事：声明配置类、开启自动配置、扫描当前包及子包。所以启动类放的位置很关键，它决定默认扫描范围。

如果 Controller 或 Service 放到了启动类包的外面，默认就扫不到，接口自然可能四零四或 Bean 注入失败。run 方法先创建 Spring Application，推断应用类型，准备环境，读取命令行参数、环境变量、application 点 properties 或 yml、profile 配置。然后创建 Application Context。Servlet 应用通常用 AnnotationConfigServletWebServerApplicationContext。接着加载 Bean 定义，执行自动配置。自动配置不是无条件生效，而是按 classpath、已有 Bean、配置项等条件判断。

较新版本会读取 auto-configuration-imports 文件，列出候选配置类，再用条件注解决定谁生效。比如引入 spring-boot-starter-web，类路径里有 Spring MVC 和内嵌 Tomcat，默认就会准备 Web 服务器。刷新上下文是核心阶段，它会实例化单例 Bean，完成依赖注入，执行初始化方法，处理 AOP 代理，发布事件。顺序很重要，Controller 依赖 Service，Service 依赖 Repository，都是在这里装配起来。如果某个 Bean 创建失败，应用通常会在启动时直接报错，而不是等你访问接口才发现。配置错误、循环依赖、数据库连不上，都可能在这个阶段暴露。Web 服务器怎么起？

刷新后期，Spring Boot 会创建 Web Server，默认内嵌 Tomcat，绑定端口，通常是八零八零，同时注册 Dispatcher Servlet，把请求交给 Spring MVC。到这里，服务才真正监听网络，你会看到 started application 日志。如果使用 WebFlux，则可能是 Netty，模型不同，但启动思想类似。端口被占用、绑定地址错误，也会在这一步失败。请求进来后，Tomcat 接收 TCP 连接，解析 HTTP，交给 Dispatcher Servlet。它根据 URL 找 Handler Mapping，匹配到 Controller 方法。参数解析器把路径、查询参数、请求体 JSON 转成方法参数。

Controller 调 Service，Service 调 Repository，访问数据库或缓存。返回值再由 HttpMessageConverter 转成 JSON，最后写回响应。整个过程围绕 Spring 容器里的 Bean 展开。启动完成后，ApplicationRunner 和 CommandLineRunner 会执行，适合做缓存预热、数据校验，但别放太重任务，否则会拖慢可用时间。生产环境还要关注端口、线程池、数据库连接池、健康检查和优雅停机。Actuator 可以暴露健康状态和指标，让你知道服务是不是真的可用了。为什么能一行启动？因为 Spring Boot 把传统 Java Web 应用的复杂部署标准化了。内嵌容器，省去外装 Tomcat；

starter 管理依赖，自动配置提供默认行为，外部化配置适配环境。它不是跳过 Spring，而是把 Spring 的配置和启动流程封装成可预测的默认路径。但默认不等于永远正确。自动配置只在条件满足时生效，扫描范围由启动类包位置决定，配置优先级会覆盖默认值，不同版本和 starter 组合也会改变行为。排查启动问题可以按入口、配置、Bean、Web 服务器、请求链路顺序看，通常很快能定位。所以 Spring Boot 后端服务跑起来，本质是 main 方法触发上下文刷新，自动配置装配组件，内嵌服务器监听端口，最终处理 HTTP 请求。内嵌 Web 服务器监听端口，Dispatcher Server 分发请求。掌握这条主线，你看到的不再是黑盒，而是一条从代码到网络服务的清晰流水线。
