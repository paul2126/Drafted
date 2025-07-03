// 리스트 항목들 분리
import { StateButton } from "../components/";
import { Link } from "react-router-dom";

export const ApplicationRow = ({ applications }) => {
  return (
    <div className="space-y-px">
      {applications.map((app, index) => (
        <div key={app.id}>
          <div className="flex items-center py-5">
            {/* Checkbox */}
            <div className="w-[75px] flex justify-center">
              <div className="w-[35px] h-[35px] rounded-[5px] border-2 border-black bg-white" />
            </div>

            {/* Application Title */}
            <Link to="/storylinedetail">
              <div className="w-[500px] px-2 flex justify-center">
                <span className="text-[20px] text-black text-center">
                  {app.title}
                </span>
              </div>
            </Link>

            {/* Deadline */}
            <div className="w-[180px] px-2 flex justify-center">
              <span className="text-[20px]  text-black text-center">
                {app.deadline}
              </span>
            </div>

            {/* Category */}
            <div className="w-[250px] px-2 flex justify-center">
              <span className="text-[20px]  text-black text-center whitespace-pre-line">
                {app.category}
              </span>
            </div>

            {/* Status */}
            <StateButton key={app.id} app={app} />
          </div>

          {/* Divider line (except for last item) */}
          {index < applications.length - 1 && (
            <div className="h-[2px] bg-black" />
          )}
        </div>
      ))}
    </div>
  );
};
