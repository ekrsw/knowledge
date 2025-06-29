import React, { useState } from 'react';
import { ArrowLeft, CheckCircle, X, Edit } from 'lucide-react';
import { FAQ } from '../../types';
import { mockApprovalGroups } from '../../data/mockData';
import { FAQDetail } from '../FAQ/FAQDetail';

interface ApprovalFormProps {
  faq: FAQ;
  onApprove: (faq: FAQ, comment: string, approvalGroup: string) => void;
  onReject: (faq: FAQ, reason: string) => void;
  onEdit: (faq: FAQ) => void;
  onBack: () => void;
}

export const ApprovalForm: React.FC<ApprovalFormProps> = ({
  faq,
  onApprove,
  onReject,
  onEdit,
  onBack,
}) => {
  const [approvalComment, setApprovalComment] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [selectedApprovalGroup, setSelectedApprovalGroup] = useState(faq.approvalGroup || '');
  const [showRejectForm, setShowRejectForm] = useState(false);

  const handleApprove = () => {
    onApprove(faq, approvalComment, selectedApprovalGroup);
  };

  const handleReject = () => {
    onReject(faq, rejectionReason);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <button
              onClick={onBack}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="mr-2" size={20} />
              承認待ち一覧に戻る
            </button>
            <h2 className="text-xl font-bold text-gray-900">FAQ承認</h2>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div>
              <span className="text-sm font-medium text-blue-700">投稿者:</span>
              <span className="ml-2 text-blue-900">{faq.authorName}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-blue-700">投稿日:</span>
              <span className="ml-2 text-blue-900">{formatDate(faq.createdAt)}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-blue-700">種別:</span>
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                新規投稿
              </span>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              承認グループ
            </label>
            <select
              value={selectedApprovalGroup}
              onChange={(e) => setSelectedApprovalGroup(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">選択してください</option>
              {mockApprovalGroups.map((group) => (
                <option key={group.id} value={group.name}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              承認コメント
            </label>
            <textarea
              value={approvalComment}
              onChange={(e) => setApprovalComment(e.target.value)}
              rows={3}
              placeholder="承認に関するコメントがあれば入力してください"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {showRejectForm && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <label className="block text-sm font-medium text-red-700 mb-2">
                却下理由 <span className="text-red-500">*</span>
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                rows={3}
                placeholder="却下する理由を入力してください"
                className="w-full px-4 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              />
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => onEdit(faq)}
              className="flex items-center justify-center px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Edit className="mr-2" size={18} />
              編集
            </button>
            <button
              onClick={handleApprove}
              disabled={!selectedApprovalGroup}
              className="flex items-center justify-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <CheckCircle className="mr-2" size={18} />
              承認
            </button>
            {!showRejectForm ? (
              <button
                onClick={() => setShowRejectForm(true)}
                className="flex items-center justify-center px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <X className="mr-2" size={18} />
                却下
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleReject}
                  disabled={!rejectionReason.trim()}
                  className="flex items-center justify-center px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  却下確定
                </button>
                <button
                  onClick={() => {
                    setShowRejectForm(false);
                    setRejectionReason('');
                  }}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  キャンセル
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <FAQDetail faq={faq} onBack={() => {}} />
    </div>
  );
};