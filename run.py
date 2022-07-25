import obj_manager
import model_handler2

if __name__ == '__main__':
    obj_manager.initialize()
    manager = obj_manager.ModelViewManager()
    print(manager.list_models() )
    print(manager.list_views() )
    print(manager.list_views("iJO1366"))
    print(manager.model_property("iJO1366"))

    mh = model_handler2.ModelHandler2()
    iJO1366_path = manager.model_property("iJO1366")["path"]
    mh.set_base_model("iJO1366", iJO1366_path)
    mh.do_FBA()
    print("========================================")
    mh.add_modification_command(["knockout", "DHAtex"])
    mh.do_FBA()
    print("========================================")
    mh.set_author("Taro Yamada")
    mh.save_user_model("./data/test13.yaml")
    manager.register_model("test13", "./data/test13.yaml", "iJO1366")
    print(manager.list_user_models() )