import type { SVGProps } from "react";

export type IconName =
  | "brand"
  | "dashboard"
  | "property"
  | "license"
  | "status"
  | "support"
  | "audit"
  | "trust"
  | "briefing"
  | "citizen"
  | "search"
  | "menu"
  | "collapse"
  | "expand"
  | "summary"
  | "pending"
  | "calendar"
  | "warning"
  | "documents"
  | "activity"
  | "refresh"
  | "upload"
  | "denied"
  | "notFound";

const iconPaths: Record<IconName, JSX.Element> = {
  brand: (
    <>
      <path d="M5 18.5V8.5L12 4l7 4.5v10" />
      <path d="M8.5 18.5V12h7v6.5" />
      <path d="M9 8.5h6" />
    </>
  ),
  dashboard: (
    <>
      <rect x="4.5" y="4.5" width="6.5" height="6.5" rx="1.5" />
      <rect x="13" y="4.5" width="6.5" height="10" rx="1.5" />
      <rect x="4.5" y="13" width="6.5" height="6.5" rx="1.5" />
      <rect x="13" y="16" width="6.5" height="3.5" rx="1.5" />
    </>
  ),
  property: (
    <>
      <path d="M3.5 10.5L12 4l8.5 6.5" />
      <path d="M6 9.5v10h12v-10" />
      <path d="M10 19.5v-5h4v5" />
    </>
  ),
  license: (
    <>
      <path d="M7 4.5h7l4 4v11H7z" />
      <path d="M14 4.5v4h4" />
      <path d="M9.5 13h6" />
      <path d="M9.5 16h4.5" />
    </>
  ),
  status: (
    <>
      <path d="M5 12h3l2-4 4 8 2-4h3" />
      <path d="M4 18.5h16" />
    </>
  ),
  support: (
    <>
      <circle cx="12" cy="12" r="2.5" />
      <path d="M12 4.5v2.2" />
      <path d="M12 17.3v2.2" />
      <path d="M4.5 12h2.2" />
      <path d="M17.3 12h2.2" />
      <path d="M6.7 6.7l1.6 1.6" />
      <path d="M15.7 15.7l1.6 1.6" />
      <path d="M17.3 6.7l-1.6 1.6" />
      <path d="M8.3 15.7l-1.6 1.6" />
    </>
  ),
  audit: (
    <>
      <path d="M8 6.5h8" />
      <path d="M8 10.5h8" />
      <path d="M8 14.5h5" />
      <circle cx="6" cy="6.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="6" cy="10.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="6" cy="14.5" r="1" fill="currentColor" stroke="none" />
      <path d="M6 18.5h12" />
    </>
  ),
  trust: (
    <>
      <path d="M12 4.5l6.5 2.5v4.5c0 4-2.8 6.5-6.5 8-3.7-1.5-6.5-4-6.5-8V7z" />
      <path d="M9.5 12.3l1.8 1.8 3.7-4.1" />
    </>
  ),
  briefing: (
    <>
      <path d="M6 5.5h12a1.5 1.5 0 0 1 1.5 1.5v10a1.5 1.5 0 0 1-1.5 1.5H6A1.5 1.5 0 0 1 4.5 17V7A1.5 1.5 0 0 1 6 5.5z" />
      <path d="M8.5 10.5h7" />
      <path d="M8.5 13.5h4.5" />
      <path d="M8.5 8h4" />
    </>
  ),
  citizen: (
    <>
      <path d="M4.5 10.5L12 4.5l7.5 6" />
      <path d="M6.5 10v8.5h11V10" />
      <path d="M9.5 18.5v-4h5v4" />
      <path d="M9 10.5h6" />
    </>
  ),
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="5.5" />
      <path d="M15 15l4.5 4.5" />
    </>
  ),
  menu: (
    <>
      <path d="M5 7h14" />
      <path d="M5 12h14" />
      <path d="M5 17h14" />
    </>
  ),
  collapse: <path d="M14.5 6.5L8.5 12l6 5.5" />,
  expand: <path d="M9.5 6.5l6 5.5-6 5.5" />,
  summary: (
    <>
      <path d="M5 18.5h14" />
      <path d="M7.5 15V9" />
      <path d="M12 15V5.5" />
      <path d="M16.5 15v-3.5" />
    </>
  ),
  pending: (
    <>
      <circle cx="12" cy="12" r="7.5" />
      <path d="M12 8v4l2.5 1.5" />
    </>
  ),
  calendar: (
    <>
      <rect x="4.5" y="6.5" width="15" height="13" rx="2" />
      <path d="M8 4.5v4" />
      <path d="M16 4.5v4" />
      <path d="M4.5 10h15" />
      <path d="M8.5 13.5h3" />
    </>
  ),
  warning: (
    <>
      <path d="M12 5l8 14H4z" />
      <path d="M12 10v4" />
      <circle cx="12" cy="17.2" r="0.8" fill="currentColor" stroke="none" />
    </>
  ),
  documents: (
    <>
      <path d="M8 5.5h7l3 3v10H8z" />
      <path d="M15 5.5v3h3" />
      <path d="M10.5 12h5" />
      <path d="M10.5 15h5" />
    </>
  ),
  activity: (
    <>
      <path d="M5 17.5l4-4 3 2 6-7" />
      <path d="M14 8.5h4v4" />
    </>
  ),
  refresh: (
    <>
      <path d="M19 12a7 7 0 1 1-2.1-5" />
      <path d="M19 5.5v5h-5" />
    </>
  ),
  upload: (
    <>
      <path d="M12 15.5v-8" />
      <path d="M8.5 10l3.5-3.5 3.5 3.5" />
      <path d="M5.5 18.5h13" />
    </>
  ),
  denied: (
    <>
      <path d="M12 4.5l6.5 2.5v4.5c0 4-2.8 6.5-6.5 8-3.7-1.5-6.5-4-6.5-8V7z" />
      <path d="M9 9l6 6" />
      <path d="M15 9l-6 6" />
    </>
  ),
  notFound: (
    <>
      <circle cx="10.5" cy="10.5" r="5.5" />
      <path d="M15 15l4.5 4.5" />
      <path d="M10.5 8.5v2.6" />
      <circle cx="10.5" cy="13.8" r="0.8" fill="currentColor" stroke="none" />
    </>
  )
};

export default function AppIcon({
  name,
  size = 20,
  strokeWidth = 1.8,
  className,
  ...props
}: SVGProps<SVGSVGElement> & { name: IconName; size?: number; strokeWidth?: number }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {iconPaths[name]}
    </svg>
  );
}
