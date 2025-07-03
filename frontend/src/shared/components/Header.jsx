import { useNavigate } from "react-router";
import logo from "@/assets/logo.png";
import { Link } from "react-router-dom";

// 현재는 props 로 로그인 여부를 받아오고 있음. 수정 필요.

export const Header = ({ isLogin }) => {
  return (
    <div className="items-center top-0 left-0 z-50 w-full justify-between mb-8">
      {/* Logo and Navigation */}
      <div className="flex justify-between">
        <Link to="/">
          <img src={logo} alt="logo" className="h-12" />
        </Link>
        {isLogin ? (
          <div className="flex gap-5">
            <button className="px-4 py-2 bg-[#e4e8ee] rounded-[20px] text-gray-600 font-medium">
              Storyboard
            </button>
            <Link to="/storyline">
              <button className="px-4 py-2 bg-[#3f80f7] rounded-[20px] text-black font-medium">
                Storyline
              </button>
            </Link>

            {/* User Profile */}
            <div className="flex items-center gap-2">
              <img
                src="https://storage.googleapis.com/tempo-image-previews/figma-exports%2Fuser_2zHSlEJBkEcQqWjXjpN0BzI5vib-1751527561598-node-I80%3A77%3B18%3A104-1751527561728.png"
                alt="User Profile"
                className="w-[35px] h-[35px] rounded-full"
              />
              <span className="text-[#3f80f7] font-medium">로그아웃</span>
            </div>
          </div>
        ) : (
          <div className="flex gap-2">
            <Link to="/storyline">
              <button className="w-32 h-10 rounded-full border border-black text-primary">
                로그인
              </button>
            </Link>
            <button className="w-32 h-10 rounded-full text-white bg-primary">
              회원가입
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
