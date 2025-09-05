export type ScanEntry = {
  protocol: string;
  port: number;
  state?: string;
  service?: string;
  product?: string;
  version?: string;
};

export type ScanResult = {
  id: number;
  ip: string;
  scan_payload: Record<string, ScanEntry[]>;
  created_at?: string;
};
