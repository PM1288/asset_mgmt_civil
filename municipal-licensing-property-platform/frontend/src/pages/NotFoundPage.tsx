import { Link } from "react-router-dom";
import ErrorState from "../components/ErrorState";

export default function NotFoundPage() {
  return (
    <div className="view-stack">
      <ErrorState
        title="Page not found"
        description="The page you requested is unavailable or no longer linked from this portal."
        icon="notFound"
        action={
          <Link className="button button-primary" to="/dashboard">
            Return to home
          </Link>
        }
      />
    </div>
  );
}
