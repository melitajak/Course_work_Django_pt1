from io import BytesIO
import os
import shutil
import subprocess
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, Http404, FileResponse
from .forms import SpadesOptionsForm
from zipfile import ZipFile

def upload_files(request):
    if request.method == 'POST':
        # deletion of directories
        if 'delete_files' in request.POST:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spades_output')
            temp_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_uploads')

            # Delete the spades_output directory
            if os.path.exists(output_dir):
                try:
                    shutil.rmtree(output_dir)
                    print("spades_output directory deleted successfully.")
                except Exception as e:
                    print(f"Error during spades_output cleanup: {str(e)}")

            # Delete the temp_uploads directory
            if os.path.exists(temp_upload_dir):
                try:
                    shutil.rmtree(temp_upload_dir)
                    print("temp_uploads directory deleted successfully.")
                except Exception as e:
                    print(f"Error during temp_uploads cleanup: {str(e)}")

            return redirect('upload_files')

        # form submission for SPAdes options
        form = SpadesOptionsForm(request.POST, request.FILES)
        if form.is_valid():
            input_type = form.cleaned_data['input_type']

            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spades_output')
            try:
                os.makedirs(output_dir, exist_ok=True)
                print("spades_output directory created.")
            except Exception as e:
                print(f"Error creating spades_output directory: {str(e)}")

            # Save the uploaded files to the temp directory
            temp_dir = "temp_uploads"
            try:
                os.makedirs(temp_dir, exist_ok=True)
                print("temp_uploads directory created.")
            except Exception as e:
                print(f"Error creating temp_uploads directory: {str(e)}")

            # SPAdes command
            spades_command = ['spades.py', '-o', output_dir, '-t', str(form.cleaned_data['threads'])]

            # Handle the file uploads based on input type
            if input_type == 'interlaced':
                interlaced_reads = request.FILES['interlaced_reads']
                interlaced_path = os.path.join(temp_dir, interlaced_reads.name)
                with open(interlaced_path, 'wb+') as destination:
                    for chunk in interlaced_reads.chunks():
                        destination.write(chunk)
                spades_command.extend(['--12', interlaced_path])

            elif input_type == 'paired':
                forward_reads = request.FILES['forward_reads']
                reverse_reads = request.FILES['reverse_reads']
                forward_path = os.path.join(temp_dir, forward_reads.name)
                reverse_path = os.path.join(temp_dir, reverse_reads.name)
                with open(forward_path, 'wb+') as destination:
                    for chunk in forward_reads.chunks():
                        destination.write(chunk)
                with open(reverse_path, 'wb+') as destination:
                    for chunk in reverse_reads.chunks():
                        destination.write(chunk)
                spades_command.extend(['-1', forward_path, '-2', reverse_path])

            elif input_type == 'unpaired':
                unpaired_reads = request.FILES['unpaired_reads']
                unpaired_path = os.path.join(temp_dir, unpaired_reads.name)
                with open(unpaired_path, 'wb+') as destination:
                    for chunk in unpaired_reads.chunks():
                        destination.write(chunk)
                spades_command.extend(['-s', unpaired_path])

            elif input_type == 'merged':
                merged_reads = request.FILES['merged_reads']
                merged_path = os.path.join(temp_dir, merged_reads.name)
                with open(merged_path, 'wb+') as destination:
                    for chunk in merged_reads.chunks():
                        destination.write(chunk)
                spades_command.extend(['--merged', merged_path])

            # options based on the form data
            if form.cleaned_data['isolate']:
                spades_command.append('--isolate')
            if form.cleaned_data['sc']:
                spades_command.append('--sc')
            if form.cleaned_data['meta']:
                spades_command.append('--meta')
            if form.cleaned_data['bio']:
                spades_command.append('--bio')
            if form.cleaned_data['corona']:
                spades_command.append('--corona')
            if form.cleaned_data['rna']:
                spades_command.append('--rna')
            if form.cleaned_data['plasmid']:
                spades_command.append('--plasmid')
            if form.cleaned_data['metaviral']:
                spades_command.append('--metaviral')
            if form.cleaned_data['metaplasmid']:
                spades_command.append('--metaplasmid')
            if form.cleaned_data['rnaviral']:
                spades_command.append('--rnaviral')
            if form.cleaned_data['iontorrent']:
                spades_command.append('--iontorrent')
            if form.cleaned_data['test']:
                spades_command.append('--test')
            if form.cleaned_data['only_error_correction']:
                spades_command.append('--only-error-correction')
            if form.cleaned_data['only_assembler']:
                spades_command.append('--only-assembler')
            if form.cleaned_data['careful']:
                spades_command.append('--careful')
            if form.cleaned_data['continue_run']:
                spades_command.append('--continue')
            if form.cleaned_data['restart_from']:
                spades_command.extend(['--restart-from', form.cleaned_data['restart_from']])
            if form.cleaned_data['checkpoints']:
                spades_command.extend(['--checkpoints', form.cleaned_data['checkpoints']])
            if form.cleaned_data['disable_gzip_output']:
                spades_command.append('--disable-gzip-output')
            if form.cleaned_data['disable_rr']:
                spades_command.append('--disable-rr')
            if form.cleaned_data['kmer_sizes'] and form.cleaned_data['kmer_sizes'] != 'auto':
                spades_command.extend(['-k', form.cleaned_data['kmer_sizes']])
            if form.cleaned_data['cov_cutoff'] and form.cleaned_data['cov_cutoff'] != 'off':
                spades_command.extend(['--cov-cutoff', form.cleaned_data['cov_cutoff']])
            if form.cleaned_data['phred_offset']:
                spades_command.extend(['--phred-offset', str(form.cleaned_data['phred_offset'])])

            # Save paths 
            request.session['spades_command'] = spades_command
            request.session['output_dir'] = output_dir
            request.session['temp_upload_dir'] = temp_dir

            print("SPAdes command:", " ".join(spades_command))

            return redirect('processing_view')

    else:
        form = SpadesOptionsForm()

    return render(request, 'upload.html', {'form': form})

def spades_generator(spades_command, temp_upload_dir):
    try:
        process = subprocess.Popen(spades_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        while True:
            output = process.stdout.readline()
            if output:
                yield f"data:{output}\n\n"
            if process.poll() is not None:
                break

        if process.returncode == 0:
            yield "data:SPAdes pipeline finished successfully.\n\n"
            # Delete temp_uploads directory
            try:
                shutil.rmtree(temp_upload_dir)
                yield "data:Temporary files cleaned up successfully.\n\n"
            except Exception as e:
                yield f"data:Error during cleanup: {str(e)}\n\n"
        else:
            yield f"data:SPAdes pipeline finished with errors. Return code: {process.returncode}\n\n"

    except Exception as e:
        yield f"data:An error occurred: {str(e)}\n\n"

def sse_view(request):
    spades_command = request.session.get('spades_command')
    output_dir = request.session.get('output_dir')
    temp_upload_dir = request.session.get('temp_upload_dir')

    if not spades_command or not output_dir or not temp_upload_dir:
        return StreamingHttpResponse("data:An error occurred. Missing session data.\n\n", content_type='text/event-stream')

    return StreamingHttpResponse(spades_generator(spades_command, temp_upload_dir), content_type='text/event-stream')

def processing_view(request):
    return render(request, 'processing.html')

def result_page(request):
    output_dir = request.session.get('output_dir')

    if not output_dir:
        return redirect('upload_files')

    # Generate a list of files 
    file_list = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            file_list.append(os.path.relpath(os.path.join(root, file), output_dir))

    return render(request, 'result.html', {
        'file_list': file_list,
        'output_dir': output_dir
    })


def download_file(request, file_name):
    output_dir = request.GET.get('output_dir')
    full_file_path = os.path.join(output_dir, file_name)

    if os.path.exists(full_file_path):
        response = FileResponse(open(full_file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(full_file_path)}'
        return response
    else:
        raise Http404("File does not exist")


#generate ZIP 
def download_all(request):
    output_dir = request.GET.get('output_dir')
    if not output_dir or not os.path.exists(output_dir):
        raise Http404("Output directory does not exist")

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_dir))

    zip_buffer.seek(0)

    response = FileResponse(zip_buffer, as_attachment=True, filename='spades_output.zip')
    return response
