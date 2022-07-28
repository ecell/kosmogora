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
    mh.set_model_name("test13")
    mh.save_user_model("./data/test13.yaml")
    manager.register_model("test13", "./data/test13.yaml", "iJO1366")

    mh2 = model_handler2.ModelHandler2() 
    #mh2.load_user_model("./data/test13.yaml") 
    print(manager.user_model_property("test13"))
    mh2.load_user_model(manager.user_model_property("test13")["path"]) 
    mh2.set_author("Mike") 
    mh2.add_modification_command(["bound", "DHAtex", 0.01, 0.05])
    mh2.save_user_model("./data/test23.yaml")
    manager.register_model("test23", "./data/test23.yaml", mh2.get_base_model_name() )
    print(manager.list_user_models() )
    print(manager.list_views())
    print(manager.list_views("iJO1366"))

    mh_sample = model_handler2.ModelHandler2()
    sample1_path = manager.model_property("sample1")["path"]
    mh_sample.set_base_model("sample1", sample1_path)
    print(mh_sample.do_FBA() )
    mh_sample.add_modification_command(["knockout", "AtoC"])
    mh_sample.set_author("Hanako")
    mh_sample.save_user_model("./data/test_sample1_a.yaml")
    manager.register_model("test_sample1_a", "./data/test_sample1_a.yaml", mh_sample.get_base_model_name() )
