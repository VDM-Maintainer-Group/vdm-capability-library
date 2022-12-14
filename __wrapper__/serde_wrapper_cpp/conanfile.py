from conans import ConanFile

class SerdeWrapperConan(ConanFile):
    name = "serde_wrapper"
    version = "0.1"
    license = "GPL-3.0"
    author = "iamhyc sudofree@163.com"
    url = "https://github.com/VDM-Maintainer-Group/vdm-capability-library"
    description = "jsonify serde_wrapper for cpp."
    #
    no_copy_source = True
    requires = "rapidjson/cci.20200410"

    def package(self):
        self.copy("*.hpp", "include")

    def package_id(self):
        self.info.header_only()
