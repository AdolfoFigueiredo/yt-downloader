import logo from "./imagens/logo.png"

const Navbar = () => {
  return (
    <div className="navbar">
        <img src={logo} alt="" />


        <nav>
          <a href="">Home</a>
          <a href="">Sobre</a>
          <a href="">Dúvidas</a>
        </nav>
        
    </div>
  )
}

export default Navbar