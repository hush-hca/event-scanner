import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "../app/page";

describe("HomePage", () => {
  it("shows the Korean dashboard shell", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "EventRadar" })).toBeTruthy();
    expect(screen.getByText("이벤트 수집 대기 중")).toBeTruthy();
  });
});
