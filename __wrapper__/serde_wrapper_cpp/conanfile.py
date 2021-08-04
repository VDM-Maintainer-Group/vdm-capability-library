from conans import ConanFile, CMake

class SerdeWrapperConan(ConanFile):
    name = "serde_wrapper"
    version = "0.1"
    license = "GPL-3.0"
    author = "iamhyc sudofree@163.com"
    #
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = "include/*", "CMakeLists.txt", "test.cpp"
    #
    no_copy_source = True
    requires = "rapidjson/cci.20200410"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        self.copy("*.hpp")

    def package_id(self):
        self.info.header_only()
