import { ReservationsPanel } from "../../pages/client/ReservationsPanel";

export function MyReservations({
  refreshKey,
  onChanged,
}: {
  refreshKey: number;
  onChanged: () => void;
}) {
  return (
    <ReservationsPanel
      refreshKey={refreshKey}
      onChanged={onChanged}
      showSearchLink={false}
    />
  );
}
