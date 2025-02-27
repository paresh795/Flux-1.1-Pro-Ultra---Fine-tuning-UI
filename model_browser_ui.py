import gradio as gr
from model_manager import ModelManager
from typing import List, Dict
import json

class ModelBrowserUI:
    def __init__(self, model_manager: ModelManager):
        self.manager = model_manager
        
    def _format_model_info(self, model) -> List[str]:
        """Format model information for the dataframe."""
        return [
            model.model_name,
            model.finetune_id,
            model.trigger_word,
            model.type.upper(),
            model.mode.capitalize(),
            str(model.rank) if model.rank else "N/A",
            str(model.iterations) if model.iterations else "N/A",
            str(model.learning_rate) if model.learning_rate else "N/A",
            model.priority.capitalize() if model.priority else "N/A",
            model.timestamp if model.timestamp else "N/A"
        ]
        
    def get_models_df(self) -> List[List[str]]:
        """Get all models formatted as a dataframe."""
        models = self.manager.list_models()
        return [self._format_model_info(model) for model in models]
    
    def refresh_models(self) -> tuple:
        """Refresh models from API and update display."""
        self.manager.refresh_models()
        models_data = self.get_models_df()
        return (
            models_data,
            "Models refreshed successfully!" if models_data else "No models found or error refreshing"
        )
    
    def create_ui(self) -> gr.Blocks:
        """Create the model browser interface."""
        with gr.Blocks(title="Model Browser") as interface:
            gr.Markdown("""
            # Model Browser
            View and manage your trained models. Click Refresh to fetch the latest models from the API.
            """)
            
            # Model list
            headers = [
                "Model Name",
                "Fine-tune ID",
                "Trigger Word",
                "Type",
                "Mode",
                "Rank",
                "Iterations",
                "Learning Rate",
                "Priority",
                "Timestamp"
            ]
            
            with gr.Row():
                with gr.Column(scale=4):
                    model_table = gr.Dataframe(
                        headers=headers,
                        datatype=["str"] * len(headers),
                        value=self.get_models_df(),
                        label="Trained Models",
                        interactive=False,
                        wrap=True
                    )
                
                with gr.Column(scale=1):
                    # Quick copy section
                    gr.Markdown("### Quick Copy")
                    selected_id = gr.Textbox(
                        label="Selected Model ID",
                        interactive=False
                    )
                    selected_trigger = gr.Textbox(
                        label="Trigger Word",
                        interactive=False
                    )
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Models", variant="primary")
                status = gr.Textbox(label="Status", interactive=False)
            
            # Model details section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Model Details")
                    selected_model = gr.JSON(
                        label="Selected Model Metadata",
                        value={}
                    )
            
            # Handle refresh
            refresh_outputs = [model_table, status]
            refresh_btn.click(
                fn=self.refresh_models,
                inputs=[],
                outputs=refresh_outputs
            )
            
            # Update details when model is selected
            def update_selection(evt: gr.SelectData, data: List[List[str]]) -> tuple:
                try:
                    row = data[evt.index[0]]  # Get the selected row
                    model_info = {
                        "Model Name": row[0],
                        "Fine-tune ID": row[1],
                        "Trigger Word": row[2],
                        "Type": row[3],
                        "Mode": row[4],
                        "Rank": row[5],
                        "Iterations": row[6],
                        "Learning Rate": row[7],
                        "Priority": row[8],
                        "Timestamp": row[9]
                    }
                    return (
                        json.dumps(model_info, indent=2),
                        row[1],  # Fine-tune ID
                        row[2]   # Trigger word
                    )
                except Exception as e:
                    print(f"Error updating selection: {e}")
                    return (
                        "{}",
                        "",
                        ""
                    )
            
            model_table.select(
                fn=update_selection,
                inputs=[model_table],
                outputs=[selected_model, selected_id, selected_trigger]
            )
            
        return interface 