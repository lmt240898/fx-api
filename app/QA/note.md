    def create_prompt_for_signal_analyst(self, data):
        """Prepares the prompt for the Signal Analyst AI."""
        
        data_for_prompt = data.copy()
        symbol = data_for_prompt['symbol']
        main_timeframe = data_for_prompt['timeframe']

        if 'cache_key' in data_for_prompt:
            del data_for_prompt['cache_key']
        if 'all_order_active' in data_for_prompt:
            del data_for_prompt['all_order_active']
        if 'active_orders_summary' in data_for_prompt:
            del data_for_prompt['active_orders_summary']
        if 'portfolio_exposure' in data_for_prompt:
            del data_for_prompt['portfolio_exposure']
        if 'account_info' in data_for_prompt:
            del data_for_prompt['account_info']
        if 'account_type_details' in data_for_prompt:
            del data_for_prompt['account_type_details']
        if 'balance_config' in data_for_prompt:
            del data_for_prompt['balance_config']
        if 'max_positions' in data_for_prompt:
            del data_for_prompt['max_positions']
        if 'pending_orders_summary' in data_for_prompt:
            del data_for_prompt['pending_orders_summary']
        if 'symbol' in data_for_prompt:
            del data_for_prompt['symbol']
        if 'timeframe' in data_for_prompt:
            del data_for_prompt['timeframe']
            
        provided_data = json.dumps(data_for_prompt, cls=CustomEncoder)

        prompt_function = prompts.get_prompt_function('prompt_signal_analyst')
        prompt_name = 'prompt_signal_analyst'
            
        if not prompt_function:
            self.logger.error(f"Prompt function '{prompt_name}' not found.")
            raise ValueError(f"Prompt function '{prompt_name}' not found.")

        params = {
            'symbol': symbol['origin_name'],
            'provided_data': provided_data,
            'main_timeframe': main_timeframe  # Thêm timeframe config
        }
        
        fmessage = prompt_function(params)
        
        return [{
            "role": "user",
            "content": fmessage
        }]
