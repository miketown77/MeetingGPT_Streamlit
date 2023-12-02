import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import textwrap
from html2image import Html2Image
import os
from htmlwebshot import WebShot

def add_br_after_characters(input_string, chars_per_line=50):
    output_string = ""

    for i in range(0, len(input_string), chars_per_line):
        output_string += input_string[i:i + chars_per_line] + "<br>"

    return output_string

def preprocess_text(input_text):
    # Replace all instances of \n with <br>
    processed_text = input_text.replace('\n', '<br>')
    return processed_text

def generate_website_visual(df, main_topics_df, engagement_df):
    meeting = str(df['meeting_id'].iloc[0])
    main_topics_df = main_topics_df.sort_values(by='Percentage', ascending=False)
    engagement_df = engagement_df.sort_values(by='Interactions', ascending=False)

    main_topics_df['Topic_Length'] = main_topics_df['Topic'].apply(len)

    # Find the maximum length
    max_length = main_topics_df['Topic_Length'].max()
    fontsize = (200-max_length)*0.1
    fontsize = max(10,fontsize)

    ordered_speakers = engagement_df.sort_values(by='Speaking Time', ascending=False)['Speakers'].tolist()

    fig = make_subplots(rows=2, cols=3, horizontal_spacing=0.02, vertical_spacing = 0.2, subplot_titles=['Abstract Summary (GPT35)', 
                                                    'Key Topics - % of Meeting (GPT35)', '% of Speaking Time by Participant (GPT35)', 
                                                    # '# of Interactions by Participant (GPT35)',
                                                    'Action Items (GPT35)', '', 'Sentiment (GPT35)'],
                      specs=[[{'type': 'scatter'}, {'type': 'bar'}, {'type': 'pie'}], [{'type': 'scatter'}, {'type': 'scatter'}, {'type': 'scatter'}]])
    
    bar_colors = px.colors.qualitative.Plotly[:len(ordered_speakers)]
    sentiment_colors = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}

    try:
        wrapped_summary = add_br_after_characters(df['Summary_Clipped'].iloc[0], chars_per_line=50)
    except:
        wrapped_summary = 'No Abstract Summary Generated'
    try:
        wrapped_action_items = preprocess_text(df['ActionItems_Clipped'].iloc[0])
    except:
        wrapped_action_items = 'No Action Items Noted'

    # Add annotations for formatted text above the figures in the top row
    text_annotation = go.layout.Annotation(
        x=0.008,  # x-coordinate of the text (0.5 means centered)
        y=0.99,  # y-coordinate of the text (adjust as needed)
        xref='paper',  # Use 'paper' for x-coordinate to refer to the entire plotting area
        yref='paper',  # Use 'paper' for y-coordinate to refer to the entire plotting area
        text=wrapped_summary,
        showarrow=False,
        font=dict(
            family='Arial',
            size=20,
            color='white'
        ),
        align='left'
    )
    fig.add_annotation(text_annotation)
    text_annotation2 = go.layout.Annotation(
        x=0.008,  # x-coordinate of the text (0.5 means centered)
        y=0.01,  # y-coordinate of the text (adjust as needed)
        xref='paper',  # Use 'paper' for x-coordinate to refer to the entire plotting area
        yref='paper',  # Use 'paper' for y-coordinate to refer to the entire plotting area
        text=wrapped_action_items,
        showarrow=False,
        font=dict(
            family='Arial',
            size=20,
            color='white'
        ),
        align='left'
    )
    fig.add_annotation(text_annotation2)

    fig.add_trace(go.Scatter(
      x=[2],
      y=[2],
      mode='text'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
      x=[2],
      y=[2],
      mode='text'
    ), row=2, col=1)

    # Add Bar Chart to 1st subplot
    fig.add_trace(go.Bar(x=main_topics_df['Topic'].tolist(),  y=main_topics_df['Percentage'].tolist(),
                       marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']), row=1, col=2)

    custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    # Add pie chart to the second subplot
    fig.add_trace(go.Pie(name='Test', labels=ordered_speakers, marker=dict(colors=custom_colors), values=engagement_df['Speaking Time'].tolist()),
                       row=1, col=3)

    fig.add_trace(go.Scatter(
      x=[2],
      y=[2],
      mode='text'
    ), row=2, col=2)

    # Add scatter plot to the fourth subplot
    fig.add_trace(go.Scatter(
      x=[2],
      y=[2],
      mode='markers+text',
      text=df['sentiment_category'].iloc[0],
      marker=dict(
          color=df['Sentiment_Color'].map(sentiment_colors),  # Map category to color using the color_map
          size=240  # Specify marker size
      ),
      textfont=dict(size=35, color='white')
    ), row=2, col=3)

    # Update layout for better visibility
    fig.update_layout(
      height=1100,
      width=1800,
      title=dict(text='MeetingGPT Summary Visuals - ' + str(df['meeting_id'].iloc[0]), font=dict(size=35)),
      legend_tracegroupgap=180,
      xaxis4=dict(domain=[0, 0.55]),  # Adjust the domain for right two subplots
      xaxis5=dict(domain=[0.8, 1.0]),  # Adjust the domain for right two subplots     
      font=dict(size=fontsize, color='white'),  # Set the font size for axis labels, legend, etc.
      plot_bgcolor='rgba(0, 0, 0, 0.8)',  # Set the background color of the entire figure
      paper_bgcolor='rgba(0, 0, 0, 0.8)'  # Set the background color of the paper
    )

    labels_to_show_in_legend = ['Test']

    for trace in fig['data']:
      if (not trace['name'] in labels_to_show_in_legend):
          trace['showlegend'] = False

    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=1, col=1)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=1, col=1)
    fig.update_layout(scene=dict(xaxis=dict(backgroundcolor='rgba(0,0,0,0)'), yaxis=dict(backgroundcolor='rgba(0,0,0,0)')))

    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=1)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=1)
    fig.update_layout(scene=dict(xaxis=dict(backgroundcolor='rgba(0,0,0,0)'), yaxis=dict(backgroundcolor='rgba(0,0,0,0)')))

    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=2)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=2)
    fig.update_layout(scene=dict(xaxis=dict(backgroundcolor='rgba(0,0,0,0)'), yaxis=dict(backgroundcolor='rgba(0,0,0,0)')))

    # Hide axes, grid, and ticks for the first subplot
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=3)
    fig.update_yaxes(showline=False, showgrid=False, zeroline=False, showticklabels=False, row=2, col=3)
    fig.update_layout(scene=dict(xaxis=dict(backgroundcolor='rgba(0,0,0,0)'), yaxis=dict(backgroundcolor='rgba(0,0,0,0)')))

    # Update subplot titles font directly in subplot_titles
    fig.update_annotations(font=dict(size=18))
    fig.update_xaxes(row=1, col=2, layer='above traces')

    # temp_directory_for_files = 'C:\\Users\\miked\\OneDrive\\Desktop\\W210\\Streamlit\\plots'

    # # Change the working directory
    # os.chdir(temp_directory_for_files)

    # file_name = str(meeting)+'_GPT.html'
    # file_name_jpg = str(meeting)+'_GPT.jpg'
    # full_file_path_jpg = os.path.join(temp_directory_for_files, file_name_jpg)


    # fig.write_html(file_name) 

    # hti = Html2Image()

    # shot = WebShot()
    # shot.quality = 100

    # img = shot.create_pic(html=file_name)

    # hti.screenshot(html_file=file_name, save_as=file_name_jpg)
    # img = hti.screenshot_as_image(file_name)
    # img = hti.screenshot_as_png(html_str=html_content)
    # img = hti.to_image(fig.to_html(full_html=False), format="png")

    return fig



