import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { AppRole, Subject } from "../types";

type AppContextValue = {
  subject: Subject;
  hasRole: (...roles: AppRole[]) => boolean;
};

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ subject, children }: { subject: Subject; children: ReactNode }) {
  const roleSet = new Set(subject.roles);

  return (
    <AppContext.Provider
      value={{
        subject,
        hasRole: (...roles) => roles.some((role) => roleSet.has(role))
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const value = useContext(AppContext);
  if (!value) {
    throw new Error("App context is not available");
  }
  return value;
}
