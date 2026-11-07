import {build} from 'esbuild';
import {cp,mkdir,readdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const modules=process.env.STUDIO_NODE_MODULES||path.join(dir,'node_modules');
await mkdir(path.join(dir,'vendor'),{recursive:true});
await build({entryPoints:[path.join(dir,'app-source.js')],bundle:true,format:'esm',minify:true,outfile:path.join(dir,'app.js'),nodePaths:[modules],legalComments:'eof'});
const pdf=path.join(modules,'pdfjs-dist');
for(const name of ['cmaps','standard_fonts','wasm'])await cp(path.join(pdf,name),path.join(dir,'vendor',name),{recursive:true});
await cp(path.join(pdf,'build/pdf.worker.min.mjs'),path.join(dir,'vendor/pdf.worker.min.mjs'));
const css=await readFile(path.join(pdf,'web/pdf_viewer.css'),'utf8');
await writeFile(path.join(dir,'vendor/text_layer.css'),css.slice(0,css.indexOf('*/')+2)+'\n'+css.slice(css.indexOf('.textLayer {'),css.indexOf('.textLayerImages {')));
await cp(path.join(pdf,'LICENSE'),path.join(dir,'vendor/PDFJS-LICENSE.txt'));
let licenses='Bundled runtime dependencies (MIT unless noted)\n\n';
async function collect(folder){for(const item of await readdir(folder,{withFileTypes:true})){if(!item.isDirectory()||item.name.startsWith('.'))continue;const pkg=path.join(folder,item.name);if(item.name.startsWith('@')){await collect(pkg);continue;}for(const name of ['LICENSE','LICENSE.md','LICENSE.txt']){try{licenses+='\n--- '+path.relative(modules,pkg)+' ---\n'+await readFile(path.join(pkg,name),'utf8')+'\n';break;}catch{}}}}
await collect(modules);await writeFile(path.join(dir,'vendor/THIRD-PARTY-LICENSES.txt'),licenses);
