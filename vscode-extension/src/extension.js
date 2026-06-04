const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');
const path = require('path');

let client;

function activate(context) {
    const pythonPath = vscode.workspace.getConfiguration('pyreact').get('pythonPath') || 'python';
    
    // Path to the python LSP script inside the pyreact compiler directory
    const serverModule = context.asAbsolutePath(path.join('..', 'pyreact', 'compiler', 'lsp.py'));
    
    const serverOptions = {
        command: pythonPath,
        args: [serverModule]
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'pyreact' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.pyreact')
        }
    };

    client = new LanguageClient(
        'pyreactLanguageServer',
        'PyReact Language Server',
        serverOptions,
        clientOptions
    );

    client.start();

    // Register live preview panel command
    let previewDisposable = vscode.commands.registerCommand('pyreact.showPreview', () => {
        const panel = vscode.window.createWebviewPanel(
            'pyreactPreview',
            'PyReact Live Preview',
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>PyReact Live Preview</title>
                <style>
                    html, body, iframe {
                        margin: 0;
                        padding: 0;
                        width: 100%;
                        height: 100%;
                        border: none;
                        background-color: white;
                    }
                </style>
            </head>
            <body>
                <iframe src="http://localhost:5000" style="width:100%; height:100%; border:none;"></iframe>
            </body>
            </html>
        `;
    });

    context.subscriptions.push(previewDisposable);
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
