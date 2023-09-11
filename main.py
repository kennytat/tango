from tango import Tango
import tempfile
import soundfile as sf
from pathlib import Path
from datetime import datetime
import os
import gradio as gr


def new_dir_now():
    now = datetime.now() # current date and time
    date_time = now.strftime("%Y%m%d%H%M")
    return date_time

def generate(prompt_text, model, steps, guidance, samples, batch_size, disable_progress):
  # print((prompt_text, model, steps, guidance, samples, batch_size, disable_progress))
  global tango
  tempdir = os.path.join(tempfile.gettempdir(),  "TTA", new_dir_now())
  Path(tempdir).mkdir(parents=True, exist_ok=True)
  print("tempdir:", tempdir)
  tango = Tango(os.path.join("weights", model))
  prompts = prompt_text.split("\n")
  if len(prompts) >= 1 and prompts[0]:
    audio = tango.generate(prompts[0], steps=steps, guidance=guidance, samples=samples, disable_progress=disable_progress)
    sf.write(os.path.join(tempdir, f"{prompts[0]}.wav"), audio, samplerate=16000)
    audios = tango.generate_for_batch(prompts, steps=steps, guidance=guidance, samples=samples, batch_size=batch_size, disable_progress=disable_progress)
    for index, audio in enumerate(audios):
      sf.write(os.path.join(tempdir, f"{prompts[index]}.wav"), audio, samplerate=16000)
    outputs = [os.path.join(tempdir, wav) for wav in os.listdir(tempdir) if wav.endswith('.wav')]
    return outputs
  else:
    raise Exception("Input length == 0")

## Your program start here
if __name__ == '__main__':
  models = [model for model in os.listdir("weights") if os.path.isdir(os.path.join("weights", model))]
  global tango
  tango = Tango(os.path.join("weights", models[0]))
  css = """
  .btn-active {background-color: "orange"}
  """
  app = gr.Blocks(title="Text To Audio", theme=gr.themes.Default(), css=css)
  with app:
      gr.Markdown("# Text To Audio" )
      with gr.Tabs():
          with gr.TabItem("TTA"):
              with gr.Row():
                  with gr.Column():
                      prompt_text = gr.Textbox(label="Prompt for TTA", interactive="true")
                      model = gr.Radio(label="Choose Model", value=models[0], choices=models)
                      steps_slider = gr.Slider(minimum=50, maximum=500, value=100, step=10, label='Steps')
                      guidance_slider = gr.Slider(minimum=1, maximum=10, value=3, step=1, label='Guidance')
                      sample_slider = gr.Slider(minimum=1, maximum=5, value=1, step=1, label='Samples')
                      batch_slider = gr.Slider(minimum=1, maximum=10, value=1, step=1, label='Batch Size')
                      disable_progress = gr.Checkbox(info="Should disable progress logging?", value=True, label="Disable Progress")
                  with gr.Column():
                      files_output = gr.Files(label="Audio Output")
                      with gr.Row():
                        gr.ClearButton([prompt_text, files_output])
                        btn = gr.Button(value="Generate", variant="primary")
                        btn.click(generate,
                                inputs=[prompt_text, model, steps_slider, guidance_slider, sample_slider, batch_slider, disable_progress],
                                outputs=[files_output])
  app.queue(concurrency_count=1).launch(
    # auth=("tta", "^TTA*607#"),
    show_api=False,
    debug=False,
    inbrowser=True,
    show_error=True,
    server_name="0.0.0.0",
    server_port=7899,
    share=False)
