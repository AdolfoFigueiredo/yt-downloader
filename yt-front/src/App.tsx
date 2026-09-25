import Navbar from "./components/Navbar"
import Infor from "./components/infor"
import Form from "./components/form"
import Download from "./components/download"
import './App.css'
const App = () => {
  return (
    <div className="app">
      <Navbar/>
      <Infor/>
      <Form/>
      <Download/>
    </div>
  )
}

export default App
