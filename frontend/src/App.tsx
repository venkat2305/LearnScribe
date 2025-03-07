import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { Button } from './components/ui/button'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className='bg-black min-h-screen text-white flex flex-col items-center justify-center space-y-4'>
      <Button>Hello</Button>
    </div>
  )
}

export default App
