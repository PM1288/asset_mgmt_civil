import { Link } from "react-router-dom";
import ErrorState from "./ErrorState";

export default function AccessDenied() {
  return (
    <ErrorState
      title="Access restricted"
      description="This page is reserved for authorised staff and support personnel."
      icon="denied"
      action={
        <Link className="button button-primary" to="/dashboard">
          Return to home
        </Link>
      }
    />
  );
}
