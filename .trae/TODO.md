# TODO:

- [x] 1: 修改config/model_configs.json文件，将所有${KIMI_API_KEY}替换为${MOONSHOT_API_KEY} (priority: High)
- [x] 2: 修改README.md文件，将KIMI_API_KEY环境变量示例替换为MOONSHOT_API_KEY (priority: High)
- [x] 4: 修复config.py中的属性名：将moonshot_api_base改为moonshot_base_url (priority: High)
- [x] 6: 修改agent_manager.py的initialize方法，移除对model_configs.json文件的依赖 (priority: High)
- [x] 7: 在agent_manager.py中动态构建四个模型配置（kimi_chat, kimi_expert, kimi_assistant, kimi_peer） (priority: High)
- [x] 8: 确保动态配置直接使用settings中的实际环境变量值 (priority: High)
- [x] 10: 修复AgentScope模型配置中的base_url设置，使用client_args字段 (priority: High)
- [x] 3: 验证修改完成后的文件内容正确性 (priority: Medium)
- [x] 5: 验证agent_manager.py能正确访问settings.moonshot_base_url配置 (priority: Medium)
- [x] 9: 测试修改后的配置是否能正确解决401认证错误 (priority: Medium)
