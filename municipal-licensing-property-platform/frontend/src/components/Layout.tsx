import type { ReactNode } from "react";

type Props = {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
};

export default function Layout({ title, actions, children }: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>{title}</h2>
        <div>{actions}</div>
      </div>
      <div className="panel-body">{children}</div>
    </section>
  );
}
