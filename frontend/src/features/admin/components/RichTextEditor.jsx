import { useEffect } from 'react'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

function ToolbarButton({ isActive, onClick, label }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded border px-2 py-1 text-xs font-semibold ${
        isActive ? 'border-primary bg-primary/10 text-primary' : 'border-slate-300 text-slate-700'
      }`}
    >
      {label}
    </button>
  )
}

export function RichTextEditor({ value, onChange }) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({
        openOnClick: false,
      }),
      Image,
    ],
    content: value,
    immediatelyRender: false,
    onUpdate: ({ editor: currentEditor }) => {
      onChange(currentEditor.getHTML())
    },
  })

  useEffect(() => {
    if (!editor) {
      return
    }
    const currentHtml = editor.getHTML()
    if (value !== currentHtml) {
      editor.commands.setContent(value, { emitUpdate: false })
    }
  }, [editor, value])

  if (!editor) {
    return <div className="rounded-lg border border-slate-300 p-3 text-sm text-slate-500">Memuat editor...</div>
  }

  return (
    <div className="rounded-lg border border-slate-300">
      <div className="flex flex-wrap gap-2 border-b border-slate-200 bg-slate-50 p-2">
        <ToolbarButton isActive={editor.isActive('bold')} onClick={() => editor.chain().focus().toggleBold().run()} label="Bold" />
        <ToolbarButton isActive={editor.isActive('italic')} onClick={() => editor.chain().focus().toggleItalic().run()} label="Italic" />
        <ToolbarButton isActive={editor.isActive('heading', { level: 2 })} onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} label="H2" />
        <ToolbarButton isActive={editor.isActive('bulletList')} onClick={() => editor.chain().focus().toggleBulletList().run()} label="Bullet" />
        <ToolbarButton isActive={editor.isActive('orderedList')} onClick={() => editor.chain().focus().toggleOrderedList().run()} label="Numbered" />
        <ToolbarButton isActive={editor.isActive('blockquote')} onClick={() => editor.chain().focus().toggleBlockquote().run()} label="Quote" />
      </div>
      <EditorContent editor={editor} className="min-h-44 p-3 text-sm text-slate-800 [&_.ProseMirror]:min-h-36 [&_.ProseMirror]:outline-none" />
    </div>
  )
}
